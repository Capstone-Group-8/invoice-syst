"""
Invoice Extractor
OCR text grouping, invoice field parsing, and confidence scoring
"""

import re
import statistics




PRODUCT_ID_PATTERN = re.compile(
    r"^\d{6}-[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+$"
)
PRODUCT_ID_START_PATTERN = re.compile(r"^\d{6}-")
HS_CODE_PATTERN = re.compile(r"^\d{4}\.\d{2}$")
MONEY_PATTERN = re.compile(r"^\$?\d[\d,]*\.\d{2}$")
INTEGER_PATTERN = re.compile(r"^\d+$")

HEADER_WORDS = {
    "quantity", "item", "description", "hs", "code", "rate", "amount"
}


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def compact_text(text):
    return re.sub(r"\s+", "", clean_text(text))


def safe_number(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def parse_number(text):
    value = compact_text(text).replace("$", "").replace(",", "")
    try:
        return float(value)
    except ValueError:
        return None


def looks_like_product_id(text):
    return bool(PRODUCT_ID_PATTERN.fullmatch(compact_text(text)))


def starts_like_product_id(text):
    return bool(PRODUCT_ID_START_PATTERN.match(compact_text(text)))


def looks_like_hs_code(text):
    return bool(HS_CODE_PATTERN.fullmatch(compact_text(text)))


def looks_like_money(text):
    return bool(MONEY_PATTERN.fullmatch(compact_text(text)))


def row_center_y(row):
    if not row:
        return 0.0
    return statistics.mean(
        safe_number(item.get("y")) + safe_number(item.get("height")) / 2
        for item in row if item
    )


def group_page(results):
    """Group OCR boxes into visual rows using their coordinates."""
    if not results:
        return []

    heights = [safe_number(r.get("height"), 0) for r in results if safe_number(r.get("height"), 0) > 0]
    if not heights:
        return []

    median_height = statistics.median(heights)
    rows = []

    for result in sorted(results, key=lambda r: (safe_number(r.get("y")), safe_number(r.get("x")))):
        center_y = safe_number(result.get("y")) + safe_number(result.get("height")) / 2
        best_row = None
        best_distance = None

        for row in rows:
            distance = abs(center_y - row_center_y(row))
            allowed = max(median_height * 0.65, safe_number(result.get("height")) * 0.55)
            if distance <= allowed and (best_distance is None or distance < best_distance):
                best_row = row
                best_distance = distance

        if best_row is None:
            rows.append([result])
        else:
            best_row.append(result)

    for row in rows:
        row.sort(key=lambda r: safe_number(r.get("x")))

    rows.sort(key=row_center_y)
    return rows


def remove_duplicate_results(results):
    unique = []
    seen = set()

    for result in results:
        text = clean_text(result.get("text", "")).lower()
        key = (
            result.get("page", 1),
            text,
            round(safe_number(result.get("x")), 1),
            round(safe_number(result.get("y")), 1),
        )
        if key not in seen:
            seen.add(key)
            unique.append(result)

    return unique


def combine_wrapped_product_ids(rows):
    """Re-join a product ID that OCR split across two visual rows."""
    if not rows:
        return []

    output = []
    i = 0

    while i < len(rows):
        current = rows[i]
        partial_index = None

        for idx, item in enumerate(current):
            value = compact_text(item.get("text", ""))
            if starts_like_product_id(value) and not looks_like_product_id(value):
                partial_index = idx
                break

        if partial_index is None or i + 1 >= len(rows):
            output.append(current)
            i += 1
            continue

        partial = current[partial_index]
        next_row = rows[i + 1]

        candidates = []
        for idx, item in enumerate(next_row):
            value = compact_text(item.get("text", ""))
            if not value or len(value) > 12:
                continue

            x_distance = abs(safe_number(item.get("x")) - safe_number(partial.get("x")))
            y_distance = abs(row_center_y(next_row) - row_center_y(current))

            if x_distance <= max(150, safe_number(partial.get("width")) * 2) and y_distance <= max(
                safe_number(partial.get("height")) * 2, 30
            ):
                candidates.append((x_distance, idx, item))

        if not candidates:
            output.append(current)
            i += 1
            continue

        _, continuation_index, continuation = min(candidates, key=lambda x: x[0])
        combined = compact_text(partial.get("text", "")) + compact_text(continuation.get("text", ""))

        if not looks_like_product_id(combined):
            output.append(current)
            i += 1
            continue

        repaired = dict(partial)
        repaired["text"] = combined
        repaired["confidence"] = min(
            safe_number(partial.get("confidence")),
            safe_number(continuation.get("confidence")),
        )

        new_current = [item for idx, item in enumerate(current) if idx != partial_index]
        new_current.append(repaired)
        new_current.sort(key=lambda r: safe_number(r.get("x")))
        output.append(new_current)

        remaining = [item for idx, item in enumerate(next_row) if idx != continuation_index]
        if remaining:
            output.append(remaining)

        i += 2

    return output


def group_text(results):
    """Group all OCR results by page and visual row."""
    if not results:
        return []

    results = remove_duplicate_results(results)
    pages = {}

    for result in results:
        pages.setdefault(result.get("page", 1), []).append(result)

    all_rows = []
    for page in sorted(pages):
        rows = group_page(pages[page])
        rows = combine_wrapped_product_ids(rows)
        all_rows.extend(rows)

    return all_rows


def clamp(value):
    return max(0.0, min(1.0, float(value)))


def product_id_format_score(suppliers_id):
    return 1.0 if suppliers_id and looks_like_product_id(suppliers_id) else 0.0


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


def find_product_anchor(row):
    for item in row:
        if looks_like_product_id(item.get("text", "")):
            return item
    return None


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

            if row_index == 0 and item["x"] < product_item["x"]:
                if INTEGER_PATTERN.fullmatch(compact_text(text)):
                    continue

            if looks_like_product_id(text):
                continue

            if re.fullmatch(r"\d+\s+of\s+\d+", lower):
                continue

            parts.append(text)

    return " ".join(parts).strip()


def parse_line_items(rows):
    anchors = []
    for index, row in enumerate(rows):
        product_item = find_product_anchor(row)
        if product_item is not None:
            anchors.append((index, product_item))

    line_items = []

    for pos, (start, product_item) in enumerate(anchors):
        end = anchors[pos + 1][0] if pos + 1 < len(anchors) else len(rows)
        item_rows = rows[start:end]
        suppliers_id = compact_text(product_item["text"])
        quantity = None
        quantity_candidates = []
        for item in rows[start]:
            if item is product_item:
                continue
            text = compact_text(item.get("text", ""))
            if not INTEGER_PATTERN.fullmatch(text):
                continue
            if item["x"] < product_item["x"]:
                quantity_candidates.append((product_item["x"] - item["x"], item))
        if quantity_candidates:
            _, quantity_item = min(quantity_candidates, key=lambda c: c[0])
            quantity = int(parse_number(quantity_item["text"]))

        fields = find_fields_in_item(item_rows, product_item)
        description = build_description(item_rows, product_item, fields)
        ocr_confidence = float(product_item.get("confidence", 0))
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