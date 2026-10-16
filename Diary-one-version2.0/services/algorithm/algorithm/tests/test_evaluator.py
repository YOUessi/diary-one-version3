import unittest

from diary_one_ci.core import boundary_metrics


class EvalV01SyntheticTests(unittest.TestCase):
    def test_ev001_exact_match(self):
        self.assertEqual(boundary_metrics([1000], [1000])["f1"], 1.0)

    def test_ev002_tolerance_match(self):
        self.assertEqual(boundary_metrics([1000], [1999])["tp"], 1)

    def test_ev003_outside_tolerance(self):
        self.assertEqual(boundary_metrics([1000], [2001])["tp"], 0)

    def test_ev004_no_gold_no_prediction(self):
        self.assertEqual(boundary_metrics([], [])["f1"], 1.0)

    def test_ev005_missed_boundary(self):
        self.assertEqual(boundary_metrics([1000], [])["boundary_miss_rate"], 1.0)

    def test_ev006_false_positive(self):
        self.assertEqual(boundary_metrics([], [1000])["fp"], 1)

    def test_ev007_one_to_one_matching(self):
        self.assertEqual(boundary_metrics([1000, 1100], [1050])["tp"], 1)

    def test_ev008_order_independent(self):
        self.assertEqual(boundary_metrics([3000, 1000], [1000, 3000])["f1"], 1.0)

