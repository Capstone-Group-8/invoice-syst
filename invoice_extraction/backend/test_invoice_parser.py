"""
Test Invoice Extractor
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from invoice_parser import (
    calculate_confidence,
    clean_text,
    combine_wrapped_product_ids,
    compact_text,
    confidence_level,
    find_fields_in_item,
    group_text,
    looks_like_product_id,
    math_validation,
    parse_invoice_fields,
    parse_invoice_metadata,
    parse_line_items,
    product_id_format_score,
    starts_like_product_id,
)


def box(text, x, y, width=40, height=20, confidence=0.95, page=1):
    """Build an OCR-box dict matching ocr_reader.process_ocr_results()'s shape."""
    return {
        "text": text,
        "confidence": confidence,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "page": page,
    }
    

class TestTextUtilities(unittest.TestCase):

    def test_clean_text_collapses_whitespace(self):
        self.assertEqual(clean_text("  hello   world \n"), "hello world")

    def test_clean_text_handles_none(self):
        self.assertEqual(clean_text(None), "")

    def test_compact_text_removes_all_whitespace(self):
        self.assertEqual(compact_text("706636 - BE - F1"), "706636-BE-F1")

    def test_looks_like_product_id(self):
        self.assertTrue(looks_like_product_id("706636-BE-F1-30cm"))
        self.assertFalse(looks_like_product_id("706636-BE"))
        self.assertFalse(looks_like_product_id("not an id"))

    def test_starts_like_product_id(self):
        self.assertTrue(starts_like_product_id("706636-BE"))
        self.assertTrue(starts_like_product_id("706636-BE-F1-30cm"))
        self.assertFalse(starts_like_product_id("BE-706636"))


class TestGroupText(unittest.TestCase):

    def test_groups_boxes_on_same_line_into_one_row(self):
        results = [
            box("Hello", x=0, y=100, height=20),
            box("World", x=60, y=102, height=20),
        ]
        rows = group_text(results)
        self.assertEqual(len(rows), 1)
        self.assertEqual([item["text"] for item in rows[0]], ["Hello", "World"])

    def test_separates_boxes_on_different_lines(self):
        results = [
            box("Line one", x=0, y=0, height=20),
            box("Line two", x=0, y=200, height=20),
        ]
        rows = group_text(results)
        self.assertEqual(len(rows), 2)

    def test_rows_are_ordered_top_to_bottom(self):
        results = [
            box("Second", x=0, y=200, height=20),
            box("First", x=0, y=0, height=20),
        ]
        rows = group_text(results)
        self.assertEqual(rows[0][0]["text"], "First")
        self.assertEqual(rows[1][0]["text"], "Second")

    def test_removes_exact_duplicate_boxes(self):
        results = [
            box("Duplicate", x=10.0, y=10.0),
            box("Duplicate", x=10.0, y=10.0),
        ]
        rows = group_text(results)
        total_boxes = sum(len(row) for row in rows)
        self.assertEqual(total_boxes, 1)

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(group_text([]), [])


class TestCombineWrappedProductIds(unittest.TestCase):

    def test_rejoins_id_split_across_two_rows(self):
        rows = [
            [box("706636-BE-F1-", x=0, y=0, width=60, height=20)],
            [box("30cm", x=10, y=25, width=40, height=20)],
        ]
        combined = combine_wrapped_product_ids(rows)
        all_text = [compact_text(item["text"]) for row in combined for item in row]
        self.assertIn("706636-BE-F1-30cm", all_text)

    def test_leaves_complete_ids_alone(self):
        rows = [
            [box("706636-BE-F1-30cm", x=0, y=0)],
            [box("Unrelated text", x=0, y=50)],
        ]
        combined = combine_wrapped_product_ids(rows)
        self.assertEqual(len(combined), 2)


class TestProductIdFormatScore(unittest.TestCase):

    def test_valid_id_scores_one(self):
        self.assertEqual(product_id_format_score("706636-BE-F1-30cm"), 1.0)

    def test_invalid_id_scores_zero(self):
        self.assertEqual(product_id_format_score("not-an-id"), 0.0)

    def test_empty_scores_zero(self):
        self.assertEqual(product_id_format_score(""), 0.0)
        self.assertEqual(product_id_format_score(None), 0.0)


class TestMathValidation(unittest.TestCase):

    def test_exact_match_scores_one(self):
        self.assertEqual(math_validation(quantity=10, rate=2.50, amount=25.00), 1.0)

    def test_small_rounding_difference_scores_high(self):
        self.assertEqual(math_validation(quantity=3, rate=1.005, amount=3.02), 0.8)

    def test_moderate_difference_scores_partial(self):
        self.assertEqual(math_validation(quantity=10, rate=2.50, amount=25.30), 0.4)

    def test_large_difference_scores_zero(self):
        self.assertEqual(math_validation(quantity=10, rate=2.50, amount=100.00), 0.0)

    def test_missing_value_scores_zero(self):
        self.assertEqual(math_validation(quantity=None, rate=2.50, amount=25.00), 0.0)

    def test_non_numeric_scores_zero(self):
        self.assertEqual(math_validation(quantity="abc", rate=2.50, amount=25.00), 0.0)


class TestCalculateConfidence(unittest.TestCase):

    def test_perfect_line_item_scores_high(self):
        score = calculate_confidence(
            ocr_confidence=0.99,
            suppliers_id="706636-BE-F1-30cm",
            quantity=10,
            rate=2.50,
            amount=25.00,
            database_match=True,
        )
        self.assertAlmostEqual(score, 0.9965, places=4)

    def test_bad_ocr_and_no_db_match_scores_low(self):
        score = calculate_confidence(
            ocr_confidence=0.2,
            suppliers_id="garbage",
            quantity=None,
            rate=None,
            amount=None,
            database_match=False,
        )
        self.assertLess(score, 0.2)

    def test_score_is_clamped_between_zero_and_one(self):
        score = calculate_confidence(
            ocr_confidence=5.0,  
            suppliers_id="706636-BE-F1-30cm",
            quantity=10,
            rate=2.50,
            amount=25.00,
            database_match=True,
        )
        self.assertLessEqual(score, 1.0)


class TestConfidenceLevel(unittest.TestCase):

    def test_high(self):
        self.assertEqual(confidence_level(0.95), "HIGH")

    def test_medium(self):
        self.assertEqual(confidence_level(0.80), "MEDIUM")

    def test_low(self):
        self.assertEqual(confidence_level(0.50), "LOW")



class TestInvoiceParsing(unittest.TestCase):

    def setUp(self):
        self.rows = [
            [box("INVOICE", x=0, y=0), box("INV1001", x=100, y=0)],
            [box("Due Date: 2024-08-01", x=0, y=30)],
            [box("Order Date Requested 2024-07-01", x=0, y=60)],
            [box("Ship Date Via Truck 2024-07-05", x=0, y=90)],
            [box("Bullseye Glass Co.", x=0, y=120)],
            [box("Total USD $126.00", x=0, y=150)],
            [
                box("Quantity", x=0, y=180), box("Item", x=50, y=180),
                box("Description", x=100, y=180), box("HS", x=300, y=180),
                box("Code", x=330, y=180), box("Rate", x=400, y=180),
                box("Amount", x=460, y=180),
            ],
            [
                box("12", x=0, y=210),
                box("706636-BE-F1-30cm", x=60, y=210, width=120),
                box("Blue Glass Sheet", x=300, y=210, width=120),
            ],
            [
                box("0512.99", x=100, y=240),
                box("10.50", x=400, y=240, confidence=0.9),
                box("126.00", x=460, y=240, confidence=0.9),
            ],
        ]

    def test_metadata_fields(self):
        metadata = parse_invoice_metadata(self.rows)
        self.assertEqual(metadata["InvoiceNumber"], "INV1001")
        self.assertEqual(metadata["DueDate"], "2024-08-01")
        self.assertEqual(metadata["OrderDate"], "2024-07-01")
        self.assertEqual(metadata["ShipDate"], "2024-07-05")
        self.assertEqual(metadata["Supplier"], "Bullseye Glass Co.")
        self.assertEqual(metadata["TotalAmt"], 126.00)

    def test_line_item_fields(self):
        rows = [row[:] for row in self.rows]
        rows[7][1]["confidence"] = 0.93

        line_items = parse_line_items(rows)
        self.assertEqual(len(line_items), 1)

        item = line_items[0]
        self.assertEqual(item["SuppliersID"], "706636-BE-F1-30cm")
        self.assertEqual(item["Quantity"], 12)
        self.assertEqual(item["HSCode"], "0512.99")
        self.assertEqual(item["Rate"], 10.50)
        self.assertEqual(item["Amount"], 126.00)
        self.assertEqual(item["Description"], "Blue Glass Sheet")
        self.assertEqual(item["OCRConfidence"], 0.93)
        self.assertAlmostEqual(item["Confidence"], 0.7755, places=4)

    def test_parse_invoice_fields_combines_both(self):
        parsed = parse_invoice_fields(self.rows)
        self.assertEqual(parsed["Invoice"]["InvoiceNumber"], "INV1001")
        self.assertEqual(len(parsed["InvoiceLineItems"]), 1)
        self.assertEqual(parsed["InvoiceLineItems"][0]["SuppliersID"], "706636-BE-F1-30cm")

    def test_no_product_id_rows_yields_no_line_items(self):
        rows_without_items = self.rows[:6]
        self.assertEqual(parse_line_items(rows_without_items), [])


class TestFindFieldsInItem(unittest.TestCase):

    def test_picks_last_money_row_as_rate_and_amount(self):
        product_item = box("706636-BE-F1-30cm", x=60, y=0, width=120)
        item_rows = [
            [product_item],
            [box("0512.99", x=100, y=30), box("10.50", x=400, y=30), box("126.00", x=460, y=30)],
        ]
        fields = find_fields_in_item(item_rows, product_item)
        self.assertEqual(fields["HSCode"], "0512.99")
        self.assertEqual(fields["Rate"], 10.50)
        self.assertEqual(fields["Amount"], 126.00)

    def test_no_money_found_returns_none(self):
        product_item = box("706636-BE-F1-30cm", x=60, y=0, width=120)
        item_rows = [[product_item]]
        fields = find_fields_in_item(item_rows, product_item)
        self.assertIsNone(fields["Rate"])
        self.assertIsNone(fields["Amount"])
        self.assertIsNone(fields["HSCode"])


if __name__ == "__main__":
    unittest.main()
