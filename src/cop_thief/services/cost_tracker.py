import json
import os
import time

from cop_thief.shared.config_loader import ConfigLoader


class CostTracker:
    def __init__(self, config: ConfigLoader):
        try:
            cfg = config._config.get("cost_tracking", {})
            self.enabled = cfg.get("enabled", True)
            self.log_path = cfg.get("log_path", "results/cost_report.json")
        except Exception:
            self.enabled = True
            self.log_path = "results/cost_report.json"
        self.calls = []

    def record_call(self, prompt_tokens: int, completion_tokens: int, model: str) -> dict:
        p_cost = (prompt_tokens / 1000.0) * 0.00015
        c_cost = (completion_tokens / 1000.0) * 0.0006
        total_cost = p_cost + c_cost

        record = {
            "timestamp": time.time(),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": total_cost,
        }
        if self.enabled:
            self.calls.append(record)
        return record

    def get_totals(self) -> dict:
        total_calls = len(self.calls)
        total_prompt = sum(c["prompt_tokens"] for c in self.calls)
        total_completion = sum(c["completion_tokens"] for c in self.calls)
        total_cost = sum(c["cost_usd"] for c in self.calls)
        return {
            "total_calls": total_calls,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_cost_usd": total_cost,
        }

    def save_report(self, path: str = None) -> None:
        if not self.enabled:
            return
        p = path or self.log_path
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"totals": self.get_totals(), "calls": self.calls}, f, indent=2)
