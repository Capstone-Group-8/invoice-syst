import os
import time
import json
from ocr_reader import extract_text
from invoice_parser import parse_invoice_fields
import shutil

DROPBOX = "C:/HW/invoice extractor/dropbox"
PROCESSED = "C:/HW/invoice extractor/processed"

os.makedirs(DROPBOX, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)

def process_file(path):
    print(f"Processing: {path}")

    lines = extract_text(path)       
    parsed = parse_invoice_fields(lines) 

    base = os.path.basename(path)
    out_path = os.path.join(PROCESSED, base + ".json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)

    shutil.move(path, os.path.join(PROCESSED, base))
    print(f"Done: {out_path}")

def watch_dropbox():
    print("Watching dropbox folder:", os.path.abspath(DROPBOX))

    while True:
        for name in os.listdir(DROPBOX):
            full = os.path.join(DROPBOX, name)
            if os.path.isfile(full):
                process_file(full)
        time.sleep(2)

if __name__ == "__main__":
    watch_dropbox()
