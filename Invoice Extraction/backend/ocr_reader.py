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
