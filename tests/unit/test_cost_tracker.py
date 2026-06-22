from unittest.mock import MagicMock

from cop_thief.services.cost_tracker import CostTracker


def test_record_call_calculates_cost_correctly():
    tracker = CostTracker(MagicMock())
    rec = tracker.record_call(1000, 1000, "gpt-4o-mini")
    assert abs(rec["cost_usd"] - 0.00075) < 1e-6


def test_get_totals_accumulates_across_calls():
    tracker = CostTracker(MagicMock())
    tracker.record_call(1000, 1000, "gpt-4o-mini")
    tracker.record_call(2000, 2000, "gpt-4o-mini")

    totals = tracker.get_totals()
    assert totals["total_calls"] == 2
    assert totals["total_prompt_tokens"] == 3000
    assert totals["total_completion_tokens"] == 3000
    assert abs(totals["total_cost_usd"] - 0.00225) < 1e-6


def test_save_report_creates_json_file(tmp_path):
    tracker = CostTracker(MagicMock())
    p = tmp_path / "test.json"
    tracker.save_report(str(p))
    assert p.exists()
