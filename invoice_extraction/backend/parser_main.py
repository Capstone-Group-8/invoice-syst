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
    for attempt in range(1, retries + 1):
        try:
            shutil.move(src, dst)
            print(f"Moved {src} → {dst}")
            return True
        except PermissionError:
            print(f"File locked, retrying ({attempt}/{retries})...")
            time.sleep(delay)

    print(f"Failed to move {src} after {retries} retries")
    return False


# Calculates an individual confidence value for each metadata field.
def calculate_metadata_confidence(parsed, ocr_results):
    invoice = parsed.get("Invoice", {})

    metadata_values = [
        invoice.get("InvoiceNumber"),
        invoice.get("Supplier"),
        invoice.get("OrderDate"),
        invoice.get("ShipDate"),
        invoice.get("DueDate"),
        invoice.get("TotalAmt"),
    ]

    metadata_confidences = []

    for value in metadata_values:
        if value in (None, "", -1):
            metadata_confidences.append(0.0)
            continue

        normalized_value = (
            str(value)
            .strip()
            .lower()
            .replace("$", "")
            .replace(",", "")
            .replace("usd", "")
            .strip()
        )

        matched_confidences = []

        for box in ocr_results:
            text = str(box.get("text", "")).strip().lower()
            confidence = box.get("confidence")

            if not text or not isinstance(confidence, (int, float)):
                continue

            # Keep OCR confidence within the expected 0-1 range.
            confidence = max(0.0, min(1.0, float(confidence)))

            normalized_text = (
                text
                .replace("$", "")
                .replace(",", "")
                .replace("usd", "")
                .strip()
            )

            # Match this individual metadata value against OCR text.
            if normalized_value and normalized_value in normalized_text:
                matched_confidences.append(confidence)

        # Use the highest confidence found for this metadata field.
        metadata_confidences.append(
            max(matched_confidences) if matched_confidences else 0.0
        )

    return metadata_confidences


# Formats a confidence score for output.
def format_confidence(value):
    if isinstance(value, (int, float)):
        return f"{value:.2f} ({confidence_level(value)})"
    return "N/A"


# --- TXT report (new): human-readable copy of the parsed invoice ---
# Missing values and negative placeholder values print as N/A instead.
def format_money(value):
    return f"${value:,.2f}" if isinstance(value, (int, float)) and value >= 0 else "N/A"


# Builds the text report line by line: the invoice details first
def write_text_report(parsed, path):
    inv = parsed["Invoice"]

    lines = [
        f"File:              {parsed.get('FileName', '')}",
        f"Invoice number:    {inv['InvoiceNumber'] or 'N/A'}",
        f"Supplier:          {inv['Supplier'] or 'N/A'}",
        f"Order date:        {inv['OrderDate'] or 'N/A'}",
        f"Ship date:         {inv['ShipDate'] or 'N/A'}",
        f"Due date:          {inv['DueDate'] or 'N/A'}",
        f"Total:             {format_money(inv['TotalAmt'])}",
        f"Metadata confidence: {format_confidence(inv.get('Confidence'))}",
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


# Handles one PDF from start to finish: reads it with OCR and parses the invoice
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
        # Run OCR on the PDF to get every piece of text with its position
        # and confidence score.
        print("Step 1: Running OCR...")
        ocr_results = extract_text(path)

        # Group the pieces of text into rows the way they appear on the page
        print("Step 2: Grouping text...")
        rows = group_text(ocr_results)

        # Read the invoice number, dates, total and line items out of those rows
        print("Step 3: Parsing invoice fields...")
        parsed = parse_invoice_fields(rows)
        parsed["FileName"] = base

        # Calculate individual metadata confidence values.
        # Each metadata field gets its own highest matching OCR confidence.
        metadata_confidence = calculate_metadata_confidence(
            parsed,
            ocr_results
        )

        parsed["Invoice"]["OCRConfidence"] = metadata_confidence
        parsed["Invoice"]["Confidence"] = metadata_confidence

        print(
            f"Metadata confidence: "
            f"{metadata_confidence}"
        )

        # Save the parsed data as a JSON file and as a readable TXT file
        print("Step 4: Writing JSON and TXT...")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)

        write_text_report(parsed, out_txt)

        # Move the PDF into processed/, replacing an older copy
        # of the same name if there is one.
        print("Step 5: Moving PDF...")

        if os.path.exists(processed_pdf):
            os.remove(processed_pdf)

        if safe_move(path, processed_pdf):
            print(
                f"SUCCESS: {base} moved to processed, "
                f"JSON written at {out_json}, "
                f"TXT written at {out_txt}"
            )
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
TEMP_NAME_PATTERNS = (
    ".tmp",
    ".temp",
    ".part",
    ".crdownload",
    ".download",
)


# Decides whether a file name looks like a temp file.
def is_temp_file(name):
    lower = name.lower()

    if lower.startswith(".") or lower.startswith("~$") or lower.startswith("~"):
        return True

    if any(lower.endswith(suffix) for suffix in TEMP_NAME_PATTERNS):
        return True

    if "tmp" in lower or "temp" in lower:
        return True

    return False


# Waits until the file exists and has finished copying.
def receive_file(filepath):
    while not os.path.isfile(filepath) or not file_is_ready(filepath):
        time.sleep(100)

    name = os.path.basename(filepath)

    return process_file(filepath)


# Runs forever, checking the dropbox folder once a second
# and processing any new PDFs.
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
                    print(
                        f"Could not delete stray temp file "
                        f"{name}: {error}"
                    )
                continue

            # Ignore anything that isn't a PDF
            if not name.lower().endswith(".pdf"):
                continue

            # Skip files that are still being copied;
            # they get picked up on the next pass.
            if not file_is_ready(full):
                continue

            # Run the PDF through OCR, parsing and output
            process_file(full)

        time.sleep(1)


# Start watching the dropbox when this file is run directly
if __name__ == "__main__":
    watch_dropbox()
