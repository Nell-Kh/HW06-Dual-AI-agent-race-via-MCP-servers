import json
import os

from cop_thief.services.report_generator import ReportGenerator
from cop_thief.shared.config_loader import ConfigLoader


def test_build_report_has_required_keys():
    config = ConfigLoader()
    config._config = {"report": {}}
    gen = ReportGenerator(config)
    report = gen.build_report([], 10, 5)
    assert gen.validate_report(report)


def test_totals_match_sub_game_sum():
    config = ConfigLoader()
    config._config = {"report": {}}
    gen = ReportGenerator(config)
    sub_games = [
        {"cop_score": 10, "thief_score": 5},
        {"cop_score": 10, "thief_score": 0},
    ]
    report = gen.build_report(sub_games, 20, 5)
    assert report["totals"]["cop"] == 20
    assert report["totals"]["thief"] == 5


def test_validate_report_passes():
    config = ConfigLoader()
    config._config = {"report": {}}
    gen = ReportGenerator(config)
    report = gen.build_report([], 0, 0)
    assert gen.validate_report(report)


def test_save_report_creates_file(tmp_path):
    config = ConfigLoader()
    config._config = {"report": {}}
    gen = ReportGenerator(config)
    report = gen.build_report([], 0, 0)
    p = os.path.join(tmp_path, "report.json")
    gen.save_report(report, p)
    assert os.path.exists(p)
    with open(p) as f:
        data = json.load(f)
    assert data == report
