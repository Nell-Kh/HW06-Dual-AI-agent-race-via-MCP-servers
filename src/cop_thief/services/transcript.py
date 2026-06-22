import json
import os
import time

from cop_thief.shared.config_loader import ConfigLoader


class TranscriptWriter:
    def __init__(self, config: ConfigLoader):
        try:
            self.log_path = "results/transcript.jsonl"
        except Exception:
            self.log_path = "results/transcript.jsonl"
        self.moves = []

    def record_move(
        self,
        sub_game: int,
        turn: int,
        agent_name: str,
        observation: str,
        action: str,
        dialogue: str,
    ) -> None:
        record = {
            "sub_game": sub_game,
            "turn": turn,
            "agent": agent_name,
            "observation": observation,
            "action": action,
            "dialogue": dialogue,
            "timestamp": time.time(),
        }
        self.moves.append(record)

    def get_transcript(self) -> list:
        return self.moves

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            for m in self.moves:
                f.write(json.dumps(m) + "\n")
