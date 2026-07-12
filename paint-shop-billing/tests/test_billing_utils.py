import unittest

from app.billing import InvoiceLineInput, build_product_search_text, calculate_invoice, matches_product_search


class BillingUtilsTests(unittest.TestCase):
    def test_calculates_gst_invoice(self):
        lines, summary = calculate_invoice(
            [
                InvoiceLineInput(
                    product_id=1,
                    name="Rallison Ultra White",
                    quantity=2,
                    unit_price=280.0,
                    gst_percent=18.0,
                    discount=10.0,
                )
            ],
            "GST",
        )
        self.assertEqual(len(lines), 1)
        self.assertAlmostEqual(lines[0].taxable_value, 550.0)
        self.assertAlmostEqual(lines[0].gst_amount, 99.0)
        self.assertAlmostEqual(summary.cgst, 49.5)
        self.assertAlmostEqual(summary.sgst, 49.5)
        self.assertAlmostEqual(summary.round_off, 0.0)
        self.assertAlmostEqual(summary.grand_total, 649.0)

    def test_non_gst_zeroes_tax(self):
        _, summary = calculate_invoice(
            [
                InvoiceLineInput(
                    product_id=1,
                    name="Putty",
                    quantity=1,
                    unit_price=720.0,
                    gst_percent=18.0,
                )
            ],
            "NON_GST",
        )
        self.assertEqual(summary.cgst, 0.0)
        self.assertEqual(summary.sgst, 0.0)
        self.assertEqual(summary.igst, 0.0)
        self.assertEqual(summary.grand_total, 720.0)

    def test_inter_state_uses_igst(self):
        _, summary = calculate_invoice(
            [
                InvoiceLineInput(
                    product_id=1,
                    name="Primer",
                    quantity=2,
                    unit_price=100.0,
                    gst_percent=18.0,
                )
            ],
            "GST",
            "INTER_STATE",
        )
        self.assertEqual(summary.cgst, 0.0)
        self.assertEqual(summary.sgst, 0.0)
        self.assertEqual(summary.igst, 36.0)
        self.assertEqual(summary.grand_total, 236.0)

    def test_round_off_applies_to_nearest_rupee(self):
        _, summary = calculate_invoice(
            [
                InvoiceLineInput(
                    product_id=1,
                    name="Sample Item",
                    quantity=1,
                    unit_price=10.01,
                    gst_percent=18.0,
                )
            ],
            "GST",
            "INTRA_STATE",
        )
        self.assertEqual(summary.taxable_total, 10.01)
        self.assertEqual(summary.cgst, 0.9)
        self.assertEqual(summary.sgst, 0.9)
        self.assertEqual(summary.round_off, 0.19)
        self.assertEqual(summary.grand_total, 12.0)

    def test_smart_search_matches_tokens_across_fields(self):
        haystack = build_product_search_text(
            name="Ultra White",
            brand="Rallison",
            size="1L",
            shade="Ultra White",
            category="Paint",
        )
        self.assertTrue(matches_product_search("rallison 1l ultra", haystack))
        self.assertFalse(matches_product_search("nerolac 20l", haystack))


if __name__ == "__main__":
    unittest.main()
