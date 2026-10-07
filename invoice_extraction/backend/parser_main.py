"""
Capstone Group 8 - Invoice Processing System
Invoice Extractor main controller
Author: Andres Ortiz Sanchez @PlanetaryOS
"""

import json
import os
import shutil
import time

from invoice_extraction.backend.invoice_parser import (
    confidence_level,
    group_text,
    parse_invoice_fields,
)
from invoice_extraction.backend.ocr_reader import extract_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROPBOX = os.path.join(BASE_DIR, "dropbox")
PROCESSED = os.path.join(BASE_DIR, "processed")
ERRORS = os.path.join(PROCESSED, "errors")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Create the dropbox, processed, errors and temp folders if they don't exist yet
os.makedirs(DROPBOX, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)
os.makedirs(ERRORS, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


# Checks the file can be opened, then compares its size half a second apart.
def file_is_ready(path):
    try:
        with open(path, "rb"):
            pass
    except PermissionError:
        return False

    size1 = os.path.getsize(path)
    time.sleep(0.5)
    size2 = os.path.getsize(path)
    return size1 == size2


# Try moving a file with retries if it's locked by another process.
def safe_move(src: str, dst: str, retries=5, delay=2):
    for attempt in range(1, retries+1):
        try:
            shutil.move(src, dst)
            print(f"Moved {src} → {dst}")
            return True
        except PermissionError:
            print(f"File locked, retrying ({attempt}/{retries})...")
            time.sleep(delay)
    print(f"Failed to move {src} after {retries} retries")
    return False


# --- TXT report (new): human-readable copy of the parsed invoice ---
# Missing values and negative placeholder values print as N/A instead.
def format_money(value):
    return f"${value:,.2f}" if isinstance(value, (int, float)) and value >= 0 else "N/A"


# Builds the text report line by line: the invoice details first
def write_text_report(parsed, path):
    inv = parsed["Invoice"]
    # Invoice details at the top of the report
    lines = [
        f"File:            {parsed.get('FileName', '')}",
        f"Invoice number:  {inv['InvoiceNumber'] or 'N/A'}",
        f"Supplier:        {inv['Supplier'] or 'N/A'}",
        f"Order date:      {inv['OrderDate'] or 'N/A'}",
        f"Ship date:       {inv['ShipDate'] or 'N/A'}",
        f"Due date:        {inv['DueDate'] or 'N/A'}",
        f"Total:           {format_money(inv['TotalAmt'])}",
        "",
        f"Line items ({len(parsed['InvoiceLineItems'])}):",
        "-" * 60,
    ]

    # One block per line item; a quantity of -1 means none was found
    for item in parsed["InvoiceLineItems"]:
        qty = item["Quantity"] if item["Quantity"] not in (None, -1) else "N/A"
        level = confidence_level(item["Confidence"])
        lines += [
            f"#{item['LineCount']}  {item['SuppliersID']}",
            f"    Description: {item['Description'] or 'N/A'}",
            f"    Quantity:    {qty}",
            f"    HS code:     {item['HSCode'] or 'N/A'}",
            f"    Rate:        {format_money(item['Rate'])}",
            f"    Amount:      {format_money(item['Amount'])}",
            f"    Confidence:  {item['Confidence']:.2f} ({level})",
            "",
        ]

    # Save all the lines to the .txt file
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# Handles one PDF from start to finish: reads it with OCR parses the invoice
def process_file(path):
    # Work out where the PDF, JSON and TXT will be saved
    base = os.path.basename(path)
    processed_pdf = os.path.join(PROCESSED, base)
    out_json = os.path.join(PROCESSED, base + ".json")
    out_txt = os.path.join(PROCESSED, base + ".txt")

    print(f"\n=== Processing {base} ===")

    # If the file is locked or still copying, move it to errors/ and skip OCR
    if not file_is_ready(path):
        print(f"File {base} is locked, quarantining without OCR.")
        error_path = os.path.join(ERRORS, base)
        safe_move(path, error_path)
        return

    try:
        # Run OCR on the PDF to get every piece of text with its position on the page
        print("Step 1: Running OCR...")
        ocr_results = extract_text(path)

        # Group the pieces of text into rows the way they appear on the page
        print("Step 2: Grouping text...")
        rows = group_text(ocr_results)

        # Read the invoice number, dates, total and line items out of those rows
        print("Step 3: Parsing invoice fields...")
        parsed = parse_invoice_fields(rows)
        parsed["FileName"] = base

        # Save the parsed data as a JSON file and as a readable TXT file
        print("Step 4: Writing JSON and TXT...")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        write_text_report(parsed, out_txt)  # new: TXT written alongside the JSON

        # Move the PDF into processed/, replacing an older copy of the same name if there is one
        print("Step 5: Moving PDF...")
        if os.path.exists(processed_pdf):
            os.remove(processed_pdf)

        if safe_move(path, processed_pdf):
            print(f"SUCCESS: {base} moved to processed, JSON written at {out_json}, TXT written at {out_txt}")
        else:
            # The move kept failing, so try moving the PDF to errors/ instead
            error_path = os.path.join(ERRORS, base)
            if safe_move(path, error_path):
                print(f"Moved locked file to errors: {error_path}")
            else:
                print(f"ERROR: Could not move {base} even to errors")
        return parsed
    except Exception as error:
        # If any step above failed, log the error and move the PDF to errors/
        print(f"ERROR processing {base}: {error}")
        error_path = os.path.join(ERRORS, base)
        safe_move(path, error_path)



# Endings that mark a file as a temporary or partly downloaded file
TEMP_NAME_PATTERNS = (".tmp", ".temp", ".part", ".crdownload", ".download")


# Decides whether a file name looks like a temp file: it starts with . or ~,
# ends with a temp ending, or has tmp or temp anywhere in the name.
def is_temp_file(name):
    lower = name.lower()
    if lower.startswith(".") or lower.startswith("~$") or lower.startswith("~"):
        return True
    if any(lower.endswith(suffix) for suffix in TEMP_NAME_PATTERNS):
        return True
    if "tmp" in lower or "temp" in lower:
        return True
    return False

# Waits (checking every 100 seconds) until the file exists and has finished
def receive_file(filepath):
    while not os.path.isfile(filepath) or not file_is_ready(filepath):
        time.sleep(100)
    name=os.path.basename(filepath)

    return process_file(filepath)

# Runs forever, checking the dropbox folder once a second and processing any new PDFs.
def watch_dropbox():
    print("Watching dropbox folder:", os.path.abspath(DROPBOX))

    while True:
        for name in os.listdir(DROPBOX):
            full = os.path.join(DROPBOX, name)

            # Skip folders
            if not os.path.isfile(full):
                continue

            # Delete temp files instead of processing them
            if is_temp_file(name):
                try:
                    os.remove(full)
                    print(f"Deleted stray temp file: {name}")
                except OSError as error:
                    print(f"Could not delete stray temp file {name}: {error}")
                continue

            # Ignore anything that isn't a PDF
            if not name.lower().endswith(".pdf"):
                continue

            # Skip files that are still being copied; they get picked up on the next pass
            if not file_is_ready(full):
                continue

            # Run the PDF through OCR, parsing and output
            process_file(full)

        time.sleep(1)



# Start watching the dropbox when this file is run directly
if __name__ == "__main__":
    watch_dropbox()
