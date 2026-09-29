import unittest

from phase6_metrics import evaluate_rows


def row(pair_id, automated, disposition, human=""):
    return {"review_pair_id": pair_id, "automated_outcome": automated,
            "automated_evidence_disposition": disposition, "human_judgment": human}


class Phase6MetricsTests(unittest.TestCase):
    def test_entirely_unlabeled_sample_emits_no_performance_metrics(self):
        result = evaluate_rows([row("1", "no_match", "insufficient_evidence"),
                                row("2", "conflict", "supported_incompatibility")])
        self.assertEqual(result["validation_status"], "pending_human_review")
        self.assertFalse(result["performance_metrics_reported"])
        for forbidden in ("accuracy", "per_label", "confusion", "metric_denominator"):
            self.assertNotIn(forbidden, result)

    def test_partial_labels_use_only_labeled_denominator(self):
        fixture = [
            row("1", "exact_duplicate", "supported_duplicate_text", "exact_duplicate"),
            row("2", "no_match", "insufficient_evidence", "insufficient_evidence"),
            row("3", "no_match", "supported_incompatibility", "conflict"),
            row("4", "near_duplicate", "supported_near_duplicate", ""),
        ]
        result = evaluate_rows(fixture)
        self.assertEqual(result["validation_status"], "partial_human_review")
        self.assertEqual(result["metric_denominator"], 3)
        self.assertEqual(result["accuracy"], 2 / 3)
        self.assertEqual(result["confusion"]["insufficient_evidence"]["insufficient_evidence"], 1)
        self.assertEqual(result["unlabeled_rows"], 1)

    def test_invalid_human_label_fails(self):
        with self.assertRaises(ValueError):
            evaluate_rows([row("1", "no_match", "insufficient_evidence", "AI says no")])


if __name__ == "__main__":
    unittest.main()
