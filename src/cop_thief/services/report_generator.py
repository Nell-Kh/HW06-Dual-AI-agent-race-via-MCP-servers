import json
import os

from cop_thief.shared.config_loader import ConfigLoader


class ReportGenerator:
    def __init__(self, config: ConfigLoader):
        self.config = config

    def build_report(
        self, sub_game_results: list[dict], cop_score: int, thief_score: int
    ) -> dict:
        cfg = self.config.get_config().get("report", {})
        return {
            "group_name": cfg.get("group_name", "yanel11"),
            "students": [],
            "github_repo": cfg.get(
                "github_repo", "https://github.com/Nell-Kh/HW06-Dual-AI-agent-race-via-MCP-servers"
            ),
            "cop_mcp_url": "http://127.0.0.1:8001",
            "thief_mcp_url": "http://127.0.0.1:8002",
            "timezone": cfg.get("timezone", "Asia/Jerusalem"),
            "sub_games": sub_game_results,
            "totals": {"cop": cop_score, "thief": thief_score},
        }

    def validate_report(self, report: dict) -> bool:
        required_keys = [
            "group_name",
            "students",
            "github_repo",
            "cop_mcp_url",
            "thief_mcp_url",
            "timezone",
            "sub_games",
            "totals",
        ]
        return all(key in report for key in required_keys)

    def save_report(self, report: dict, path: str = "results/game_report.json") -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
