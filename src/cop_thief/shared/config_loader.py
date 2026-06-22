import json
import os
from typing import Any


class ConfigLoader:
    """Loads and validates configuration from config.json."""

    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self._config: dict[str, Any] = {}

    def load(self) -> None:
        """Reads config/config.json."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.config_path}: {e}") from e

        self.validate()

    def get_grid_size(self) -> list[int]:
        """Returns [rows, cols] as list of two positive ints."""
        grid_size = self._config["grid_size"]
        if not isinstance(grid_size, list) or len(grid_size) != 2:
            raise ValueError("grid_size must be a list of two integers")
        if not all(isinstance(x, int) and x > 0 for x in grid_size):
            raise ValueError("grid_size elements must be positive integers")
        return grid_size

    def get_max_moves(self) -> int:
        """Returns max_moves as int."""
        return int(self._config["max_moves"])

    def get_num_games(self) -> int:
        """Returns num_games as int."""
        return int(self._config["num_games"])

    def get_max_barriers(self) -> int:
        """Returns max_barriers as int."""
        return int(self._config["max_barriers"])

    def get_scoring(self) -> dict[str, int]:
        """Returns scoring dict."""
        return self._config["scoring"]

    def get_mcp_ports(self) -> dict[str, Any]:
        """Returns mcp ports dict."""
        return self._config["mcp"]

    def get_rl_config(self) -> dict[str, float]:
        """Returns rl config dict."""
        return self._config["rl"]

    def get_llm_config(self) -> dict[str, Any]:
        """Returns llm config dict."""
        return self._config["llm"]

    def get_report_config(self) -> dict[str, str]:
        """Returns report config dict."""
        return self._config["report"]

    def get_num_states(self) -> int:
        """Returns dynamically derived number of states: rows * cols."""
        rows, cols = self.get_grid_size()
        return rows * cols

    def validate(self) -> None:
        """Checks ALL required keys exist."""
        required_keys = [
            "version",
            "grid_size",
            "max_moves",
            "num_games",
            "max_barriers",
            "scoring",
            "agents",
            "llm",
            "mcp",
            "rl",
            "report",
        ]
        for key in required_keys:
            if key not in self._config:
                raise KeyError(f"Missing required config key: '{key}'")

        scoring_keys = ["cop_win", "thief_win", "cop_loss", "thief_loss"]
        for sk in scoring_keys:
            if sk not in self._config.get("scoring", {}):
                raise KeyError(f"Missing required scoring key: 'scoring.{sk}'")

        mcp_keys = ["cop_server_port", "thief_server_port", "host"]
        for mk in mcp_keys:
            if mk not in self._config.get("mcp", {}):
                raise KeyError(f"Missing required mcp key: 'mcp.{mk}'")

        rl_keys = ["learning_rate", "discount_factor", "epsilon"]
        for rk in rl_keys:
            if rk not in self._config.get("rl", {}):
                raise KeyError(f"Missing required rl key: 'rl.{rk}'")

        llm_keys = ["provider", "model", "max_tokens", "temperature"]
        for lk in llm_keys:
            if lk not in self._config.get("llm", {}):
                raise KeyError(f"Missing required llm key: 'llm.{lk}'")

        report_keys = ["recipient", "timezone", "group_name", "github_repo"]
        for rek in report_keys:
            if rek not in self._config.get("report", {}):
                raise KeyError(f"Missing required report key: 'report.{rek}'")
