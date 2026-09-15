"""
Invoice Extractor
Author: Andres Ortiz Sanchez
"""

import json
import os
import shutil
import time

from invoice_parser import parse_invoice_fields
from ocr_reader import extract_text
from text_grouper import group_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROPBOX = os.path.join(BASE_DIR, "dropbox")
PROCESSED = os.path.join(BASE_DIR, "processed")
ERRORS = os.path.join(PROCESSED, "errors")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(DROPBOX, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)
os.makedirs(ERRORS, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


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


def safe_move(src, dst, retries=5, delay=2):
    """Try moving a file with retries if it's locked by another process."""
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


def process_file(path):
    base = os.path.basename(path)
    processed_pdf = os.path.join(PROCESSED, base)
    out_json = os.path.join(PROCESSED, base + ".json")

    print(f"\n=== Processing {base} ===")

    if not file_is_ready(path):
        print(f"File {base} is locked, quarantining without OCR.")
        error_path = os.path.join(ERRORS, base)
        safe_move(path, error_path)
        return

    try:
        print("Step 1: Running OCR...")
        ocr_results = extract_text(path)

        print("Step 2: Grouping text...")
        rows = group_text(ocr_results)

        print("Step 3: Parsing invoice fields...")
        parsed = parse_invoice_fields(rows)
        parsed["FileName"] = base

        print("Step 4: Writing JSON...")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)

        print("Step 5: Moving PDF...")
        if os.path.exists(processed_pdf):
            os.remove(processed_pdf)

        if safe_move(path, processed_pdf):
            print(f"SUCCESS: {base} moved to processed, JSON written at {out_json}")
        else:
            error_path = os.path.join(ERRORS, base)
            if safe_move(path, error_path):
                print(f"Moved locked file to errors: {error_path}")
            else:
                print(f"ERROR: Could not move {base} even to errors")

    except Exception as error:
        print(f"ERROR processing {base}: {error}")
        error_path = os.path.join(ERRORS, base)
        safe_move(path, error_path)



TEMP_NAME_PATTERNS = (".tmp", ".temp", ".part", ".crdownload", ".download")


def is_temp_file(name):
    lower = name.lower()
    if lower.startswith(".") or lower.startswith("~$") or lower.startswith("~"):
        return True
    if any(lower.endswith(suffix) for suffix in TEMP_NAME_PATTERNS):
        return True
    if "tmp" in lower or "temp" in lower:
        return True
    return False


def watch_dropbox():
    print("Watching dropbox folder:", os.path.abspath(DROPBOX))

    while True:
        for name in os.listdir(DROPBOX):
            full = os.path.join(DROPBOX, name)

            if not os.path.isfile(full):
                continue

            if is_temp_file(name):
                try:
                    os.remove(full)
                    print(f"Deleted stray temp file: {name}")
                except OSError as error:
                    print(f"Could not delete stray temp file {name}: {error}")
                continue

            if not name.lower().endswith(".pdf"):
                continue

            if not file_is_ready(full):
                continue

            if not file_is_ready(full):
                print(f"File {name} still not ready after delay, skipping.")
                continue

            process_file(full)

        time.sleep(1)



if __name__ == "__main__":
    watch_dropbox()