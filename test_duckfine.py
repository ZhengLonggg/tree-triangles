import unittest

from duckfine import DuckFine


class TestDuckFineInit(unittest.TestCase):
    def test_stores_member_id(self):
        fine = DuckFine("M001")
        self.assertEqual(fine.member_id, "M001")

    def test_new_member_owes_nothing(self):
        fine = DuckFine("M001")
        self.assertEqual(fine.total_owed, 0.0)


class TestDuckFineCharge(unittest.TestCase):
    def setUp(self):
        self.fine = DuckFine("M001")

    # --- invalid input ---

    def test_negative_days_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)

    def test_negative_days_does_not_change_total_owed(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)
        self.assertEqual(self.fine.total_owed, 0.0)

    # --- grace period ---

    def test_on_time_return_is_free(self):
        self.assertEqual(self.fine.charge(0), 0.0)

    def test_one_day_late_is_within_grace(self):
        self.assertEqual(self.fine.charge(1), 0.0)

    def test_last_grace_day_is_free(self):
        self.assertEqual(self.fine.charge(2), 0.0)

    def test_first_day_after_grace_charges_daily_fee(self):
        self.assertAlmostEqual(self.fine.charge(3), 0.50)

    def test_deluxe_within_grace_is_still_free(self):
        self.assertEqual(self.fine.charge(2, deluxe=True), 0.0)

    # --- standard fees ---

    def test_fee_is_daily_rate_times_chargeable_days(self):
        # 6 days late -> 4 chargeable days * $0.50
        self.assertAlmostEqual(self.fine.charge(6), 2.00)

    def test_deluxe_doubles_the_fee(self):
        # 6 days late -> 4 chargeable days * $0.50 * 2
        self.assertAlmostEqual(self.fine.charge(6, deluxe=True), 4.00)

    # --- maximum fee cap ---

    def test_fee_exactly_at_cap_is_not_reduced(self):
        # 12 days late -> 10 chargeable days * $0.50 = $5.00
        self.assertAlmostEqual(self.fine.charge(12), 5.00)

    def test_fee_above_cap_is_capped(self):
        self.assertAlmostEqual(self.fine.charge(13), 5.00)

    def test_very_late_return_is_capped(self):
        self.assertAlmostEqual(self.fine.charge(1000), 5.00)

    def test_deluxe_fee_exactly_at_cap_is_not_reduced(self):
        # 7 days late -> 5 chargeable days * $0.50 * 2 = $5.00
        self.assertAlmostEqual(self.fine.charge(7, deluxe=True), 5.00)

    def test_deluxe_fee_above_cap_is_capped(self):
        # 8 days late -> 6 chargeable days * $0.50 * 2 = $6.00 -> capped
        self.assertAlmostEqual(self.fine.charge(8, deluxe=True), 5.00)

    # --- running total ---

    def test_charge_adds_fee_to_total_owed(self):
        self.fine.charge(6)
        self.assertAlmostEqual(self.fine.total_owed, 2.00)

    def test_free_charge_leaves_total_owed_unchanged(self):
        self.fine.charge(2)
        self.assertEqual(self.fine.total_owed, 0.0)

    def test_multiple_charges_accumulate(self):
        self.fine.charge(3)   # 0.50
        self.fine.charge(6)   # 2.00
        self.assertAlmostEqual(self.fine.total_owed, 2.50)

    def test_cap_applies_per_fine_not_to_total(self):
        self.fine.charge(100)  # 5.00
        self.fine.charge(100)  # 5.00
        self.assertAlmostEqual(self.fine.total_owed, 10.00)

    def test_members_have_independent_totals(self):
        other = DuckFine("M002")
        self.fine.charge(6)
        self.assertEqual(other.total_owed, 0.0)


if __name__ == "__main__":
    unittest.main()
