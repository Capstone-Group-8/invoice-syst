"""
Invoice Extractor
Coordinate-aware invoice line item parser
"""

import re

from confidence import calculate_confidence, confidence_level


PRODUCT_ID_PATTERN = re.compile(
    r"^\d{6}-[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+$"
)
HS_CODE_PATTERN = re.compile(r"^\d{4}\.\d{2}$")
MONEY_PATTERN = re.compile(r"^\$?\d[\d,]*\.\d{2}$")
INTEGER_PATTERN = re.compile(r"^\d+$")

HEADER_WORDS = {
    "quantity", "item", "description", "hs", "code", "rate", "amount"
}


def clean_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def compact_text(text):
    return re.sub(r"\s+", "", clean_text(text))


def parse_number(text):
    value = compact_text(text).replace("$", "").replace(",", "")
    try:
        return float(value)
    except ValueError:
        return None


def looks_like_product_id(text):
    return bool(PRODUCT_ID_PATTERN.fullmatch(compact_text(text)))


def looks_like_hs_code(text):
    return bool(HS_CODE_PATTERN.fullmatch(compact_text(text)))


def looks_like_money(text):
    return bool(MONEY_PATTERN.fullmatch(compact_text(text)))


def row_center_y(row):
    if not row:
        return 0.0
    return sum(
        item["y"] + item["height"] / 2 for item in row
    ) / len(row)


def row_min_y(row):
    return min(item["y"] for item in row) if row else 0.0


def row_max_y(row):
    return max(item["y"] + item["height"] for item in row) if row else 0.0


def find_product_anchor(row):
    for item in row:
        if looks_like_product_id(item.get("text", "")):
            return item
    return None


def find_quantity(row, product_item):
    candidates = []

    for item in row:
        if item is product_item:
            continue

        text = compact_text(item.get("text", ""))
        if not INTEGER_PATTERN.fullmatch(text):
            continue

        if item["x"] < product_item["x"]:
            candidates.append(
                (product_item["x"] - item["x"], item)
            )

    if not candidates:
        return None, None

    _, item = min(candidates, key=lambda x: x[0])
    return int(parse_number(item["text"])), item


def collect_item_rows(rows, start_index, end_index):
    return rows[start_index:end_index]


def find_fields_in_item(item_rows, product_item):
    hs_candidates = []
    money_candidates = []

    for row in item_rows:
        for item in row:
            text = compact_text(item.get("text", ""))

            if looks_like_hs_code(text):
                hs_candidates.append(item)
                continue

            if looks_like_money(text):
                money_candidates.append(item)

    hs_item = hs_candidates[-1] if hs_candidates else None
    hs_code = compact_text(hs_item["text"]) if hs_item else None

    money_candidates.sort(key=lambda item: (item["y"], item["x"]))

    rate_item = None
    amount_item = None

    if money_candidates:
        # Prefer the last visual money row.
        last_y = money_candidates[-1]["y"]
        tolerance = max(
            5.0,
            money_candidates[-1].get("height", 10) * 1.5
        )

        last_row_money = [
            item for item in money_candidates
            if abs(item["y"] - last_y) <= tolerance
        ]

        if len(last_row_money) >= 2:
            last_row_money.sort(key=lambda item: item["x"])
            rate_item = last_row_money[-2]
            amount_item = last_row_money[-1]
        elif len(money_candidates) >= 2:
            rate_item = money_candidates[-2]
            amount_item = money_candidates[-1]
        else:
            amount_item = money_candidates[-1]

    rate = parse_number(rate_item["text"]) if rate_item else None
    amount = parse_number(amount_item["text"]) if amount_item else None

    return {
        "HSCode": hs_code,
        "HSItem": hs_item,
        "Rate": rate,
        "RateItem": rate_item,
        "Amount": amount,
        "AmountItem": amount_item,
    }


def build_description(item_rows, product_item, field_data):
    excluded = {
        id(item)
        for item in (
            field_data["HSItem"],
            field_data["RateItem"],
            field_data["AmountItem"],
        )
        if item is not None
    }

    parts = []

    for row_index, row in enumerate(item_rows):
        for item in row:
            if item is product_item:
                continue
            if id(item) in excluded:
                continue

            text = clean_text(item.get("text", ""))
            if not text:
                continue

            lower = text.lower()
            if lower in HEADER_WORDS:
                continue

            # Quantity is normally before the product ID on the anchor row.
            if row_index == 0 and item["x"] < product_item["x"]:
                if INTEGER_PATTERN.fullmatch(compact_text(text)):
                    continue

            # Other product IDs mark a new item and should not happen here.
            if looks_like_product_id(text):
                continue

            # Do not put obvious page/footer data into description.
            if re.fullmatch(r"\d+\s+of\s+\d+", lower):
                continue

            parts.append(text)

    return " ".join(parts).strip()


def find_anchors(rows):
    anchors = []
    for index, row in enumerate(rows):
        product_item = find_product_anchor(row)
        if product_item is not None:
            anchors.append((index, product_item))
    return anchors


def parse_line_items(rows):
    anchors = find_anchors(rows)
    line_items = []

    for pos, (start, product_item) in enumerate(anchors):
        end = anchors[pos + 1][0] if pos + 1 < len(anchors) else len(rows)

        item_rows = collect_item_rows(rows, start, end)
        suppliers_id = compact_text(product_item["text"])

        quantity, quantity_item = find_quantity(
            rows[start],
            product_item
        )

        fields = find_fields_in_item(
            item_rows,
            product_item
        )

        description = build_description(
            item_rows,
            product_item,
            fields
        )

        ocr_confidence = float(
            product_item.get("confidence", 0)
        )

        database_match = False

        score = calculate_confidence(
            ocr_confidence=ocr_confidence,
            suppliers_id=suppliers_id,
            quantity=quantity,
            rate=fields["Rate"],
            amount=fields["Amount"],
            database_match=database_match,
        )

        line_items.append(
            {
                "SuppliersID": suppliers_id,
                "Description": description,
                "Quantity": quantity,
                "HSCode": fields["HSCode"],
                "Rate": fields["Rate"],
                "Amount": fields["Amount"],
                "OCRConfidence": round(ocr_confidence, 4),
                "Confidence": score,
            }
        )

    return line_items


def parse_invoice_metadata(rows):
    metadata = {
        "InvoiceNumber": None,
        "OrderDate": None,
        "ShipDate": None,
        "DueDate": None,
        "ShippingHandling": None,
        "TotalAmt": None,
        "Supplier": None,
    }

    for row in rows:
        text = " ".join(
            clean_text(item.get("text", ""))
            for item in row
        )

        if not metadata["InvoiceNumber"]:
            match = re.search(r"\bINV\d+\b", text, re.IGNORECASE)
            if match:
                metadata["InvoiceNumber"] = match.group(0)

        match = re.search(
            r"Due\s*Date\s*:\s*(\d{4}-\d{2}-\d{2})",
            text,
            re.IGNORECASE,
        )
        if match:
            metadata["DueDate"] = match.group(1)

        match = re.search(
            r"Order\s*Date\s+.*?(\d{4}-\d{2}-\d{2})",
            text,
            re.IGNORECASE,
        )
        if match:
            metadata["OrderDate"] = match.group(1)

        match = re.search(
            r"Ship\s*Date\s+.*?(\d{4}-\d{2}-\d{2})",
            text,
            re.IGNORECASE,
        )
        if match:
            metadata["ShipDate"] = match.group(1)

        if "Bullseye Glass Co." in text:
            metadata["Supplier"] = "Bullseye Glass Co."

        match = re.search(
            r"Total\s+USD\s+\$?([\d,]+\.\d{2})",
            text,
            re.IGNORECASE,
        )
        if match:
            metadata["TotalAmt"] = parse_number(match.group(1))

    return metadata


def parse_invoice_fields(rows):
    metadata = parse_invoice_metadata(rows)
    line_items = parse_line_items(rows)

    return {
        "Invoice": metadata,
        "InvoiceLineItems": line_items,
    }