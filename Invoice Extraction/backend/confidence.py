"""
Invoice Extractor
Line-item confidence scoring
"""

import re


PRODUCT_ID_PATTERN = re.compile(
    r"^\d{6}-[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+$"
)


def clamp(value):
    return max(0.0, min(1.0, float(value)))


def product_id_format_score(suppliers_id):
    if not suppliers_id:
        return 0.0

    value = suppliers_id.replace(" ", "").strip()
    return 1.0 if PRODUCT_ID_PATTERN.fullmatch(value) else 0.0


def math_validation(quantity, rate, amount):
    """Validate Quantity * Rate = Amount with currency rounding tolerance."""
    if quantity is None or rate is None or amount is None:
        return 0.0

    try:
        expected = round(float(quantity) * float(rate), 2)
        actual = round(float(amount), 2)
        difference = abs(expected - actual)

        if difference <= 0.01:
            return 1.0
        if difference <= 0.05:
            return 0.8
        if difference <= 0.50:
            return 0.4
        return 0.0
    except (TypeError, ValueError):
        return 0.0


def calculate_confidence(
    ocr_confidence,
    suppliers_id,
    quantity,
    rate,
    amount,
    database_match=False,
):
    """
    Weighted line-item confidence.

    OCR recognition:      35%
    Product ID format:    15%
    Inventory DB match:   20%
    Quantity/Rate/Amount: 30%
    """

    ocr_score = clamp(ocr_confidence)
    id_score = product_id_format_score(suppliers_id)
    db_score = 1.0 if database_match else 0.0
    math_score = math_validation(quantity, rate, amount)

    return round(
        clamp(
            ocr_score * 0.35
            + id_score * 0.15
            + db_score * 0.20
            + math_score * 0.30
        ),
        4,
    )


def confidence_level(score):
    score = float(score)
    if score >= 0.90:
        return "HIGH"
    if score >= 0.75:
        return "MEDIUM"
    return "LOW"