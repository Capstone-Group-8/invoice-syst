import json
import os
import shutil
import time
from pathlib import Path

from invoice_parser import parse_invoice_fields
from ocr_reader import extract_text

BASE_DIR = Path(__file__).resolve().parents[1]
DROPBOX = BASE_DIR / "dropbox"
PROCESSED = BASE_DIR / "processed"

DROPBOX.mkdir(exist_ok=True)
PROCESSED.mkdir(exist_ok=True)


def process_file(path):
    path = Path(path)
    print(f"Processing: {path}")
    lines = extract_text(str(path))
    parsed = parse_invoice_fields(lines)

    out_path = PROCESSED / f"{path.name}.json"
    with open(out_path, "w", encoding="utf-8") as output:
        json.dump(parsed, output, indent=2)

    shutil.move(str(path), str(PROCESSED / path.name))
    print(f"Done: {out_path}")


def watch_dropbox():
    print("Watching dropbox folder:", os.path.abspath(DROPBOX))
    while True:
        for name in os.listdir(DROPBOX):
            full = DROPBOX / name
            if full.is_file():
                process_file(full)
        time.sleep(2)


if __name__ == "__main__":
    watch_dropbox()
