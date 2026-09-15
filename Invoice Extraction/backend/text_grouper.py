"""
Invoice Extractor
OCR text grouping and line detection
"""
import re
import statistics

PRODUCT_ID_PATTERN = re.compile(
    r"^\d{6}-[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+$"
)
PRODUCT_ID_START_PATTERN = re.compile(r"^\d{6}-")


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def compact_text(text):
    return re.sub(r"\s+", "", clean_text(text))


def looks_like_product_id(text):
    return bool(PRODUCT_ID_PATTERN.fullmatch(compact_text(text)))


def starts_like_product_id(text):
    return bool(PRODUCT_ID_START_PATTERN.match(compact_text(text)))


def safe_number(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


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