import easyocr
import fitz  # PyMuPDF
import os

reader = easyocr.Reader(["en"], gpu=False)

def extract_text(path):
    words = []

    # PDF → images
    if path.lower().endswith(".pdf"):
        doc = fitz.open(path)

        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_path = f"temp_page_{i}.png"
            pix.save(img_path)

            # EasyOCR returns list of strings when detail=0
            results = reader.readtext(img_path, detail=0)

            # Add raw words exactly as OCR returns them
            for item in results:
                words.append(item)

            os.remove(img_path)

        doc.close()
        return words

    # Image → OCR
    else:
        results = reader.readtext(path, detail=0)
        for item in results:
            words.append(item)
        return words


def extract_text_with_confidence(path):
    """Return OCR text and EasyOCR confidence for review/flagging."""
    results_out = []

    if path.lower().endswith(".pdf"):
        doc = fitz.open(path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_path = f"temp_page_{i}.png"
            pix.save(img_path)
            results = reader.readtext(img_path, detail=1)
            for _box, text, confidence in results:
                results_out.append({"text": text, "confidence": float(confidence)})
            os.remove(img_path)
        doc.close()
    else:
        results = reader.readtext(path, detail=1)
        for _box, text, confidence in results:
            results_out.append({"text": text, "confidence": float(confidence)})

    return results_out
