import re


def parse_invoice_fields(words):
    """Return a small structured summary while preserving raw OCR text.

    This is intentionally conservative for the Alpha; vendor-specific line-item
    parsing remains an integration task.
    """
    fields = {
        "supplier": None,
        "invoice_number": None,
        "due_date": None,
        "raw_text": list(words),
    }

    for value in words:
        text = str(value).strip()
        if fields["supplier"] is None and text in {"Bullseye Glass Co.", "Mountain Glass"}:
            fields["supplier"] = text
        if fields["invoice_number"] is None:
            match = re.fullmatch(r"INV[0-9A-Za-z-]+", text)
            if match:
                fields["invoice_number"] = match.group(0)
        if fields["due_date"] is None:
            match = re.search(r"Due Date:\s*(\d{4}-\d{2}-\d{2})", text)
            if match:
                fields["due_date"] = match.group(1)

    return fields
