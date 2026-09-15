"""
Invoice Extractor
Author: Andres Ortiz Sanchez
"""

import os
import tempfile

import easyocr
import fitz
import numpy as np
from PIL import Image


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

reader = easyocr.Reader(["en"], gpu=False)


def process_ocr_results(ocr_results, page_number):
    results = []
    for bounding_box, text, confidence in ocr_results:
        x = min(point[0] for point in bounding_box)
        y = min(point[1] for point in bounding_box)
        width = max(point[0] for point in bounding_box) - x
        height = max(point[1] for point in bounding_box) - y

        results.append({
            "text": text.strip(),
            "confidence": float(confidence),
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "page": page_number
        })
    return results


def extract_text(path):
    results = []

    if path.lower().endswith(".pdf"):
        with tempfile.TemporaryDirectory(prefix="invoice_ocr_", dir=TEMP_DIR) as tmp_dir:
            with fitz.open(path) as doc:
                for page_number, page in enumerate(doc, start=1):
                    pix = page.get_pixmap(dpi=200)

                    page_path = os.path.join(tmp_dir, f"page_{page_number}.png")
                    pix.save(page_path)

                    img = Image.open(page_path).convert("RGB")
                    img_array = np.array(img)

                    ocr_results = reader.readtext(img_array, detail=1)
                    results.extend(process_ocr_results(ocr_results, page_number))
    else:
        ocr_results = reader.readtext(path, detail=1)
        results.extend(process_ocr_results(ocr_results, 1))

    return results