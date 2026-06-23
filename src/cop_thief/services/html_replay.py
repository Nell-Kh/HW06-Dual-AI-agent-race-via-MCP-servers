import json
from pathlib import Path

from cop_thief.shared.config_loader import ConfigLoader


class HTMLReplay:
    def __init__(self, config: ConfigLoader):
        self.rows, self.cols = config.get_grid_size()
        self.output_path = config.get_config().get("replay_output", "results/replay.html")
        self.frames: list[dict] = []

    def add_frame(
        self,
        sub_game: int,
        turn: int,
        agent: str,
        cop_pos: tuple[int, int],
        thief_pos: tuple[int, int],
        barriers: list[tuple[int, int]],
        action: str,
        dialogue: str,
    ) -> None:
        self.frames.append(
            {
                "sub_game": sub_game,
                "turn": turn,
                "agent": agent,
                "cop_pos": list(cop_pos),
                "thief_pos": list(thief_pos),
                "barriers": [list(b) for b in barriers],
                "action": action,
                "dialogue": dialogue,
            }
        )

    def generate_html(self, output_path: str = "") -> None:
        if not output_path:
            output_path = self.output_path

        template_path = Path(__file__).resolve().parents[3] / "assets" / "replay_template.html"
        html_template = template_path.read_text(encoding="utf-8")

        frames_json = json.dumps(self.frames)
        html = html_template.replace("{rows}", str(self.rows))
        html = html.replace("{cols}", str(self.cols))
        html = html.replace("{frames_json}", frames_json)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
