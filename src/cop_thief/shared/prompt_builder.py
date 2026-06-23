import json
import re


class PromptBuilder:
    def __init__(self, cop_persona: str, thief_persona: str):
        self.cop_persona = cop_persona
        self.thief_persona = thief_persona

    def build_cop_prompt(
        self,
        observation: str,
        valid_moves: list[str],
        history: list[str],
        barriers_remaining: int = 0,
    ) -> list[dict]:
        sys_msg = (
            "Role: Cop on 5x5 grid. Strategy: Close distance to thief. Block escape routes. "
            'Output JSON only: {"action":"up|down|left|right|up-left|up-right|'
            'down-left|down-right|place_barrier","dialogue":"quip"}'
        )
        user_msg = (
            f"Obs:{observation}\nMoves:{valid_moves}\n"
            f"Goal: Reduce distance to thief (e.g. if north go up, north-east go up-right).\n"
            f"History:{history}\n"
        )
        if barriers_remaining > 0:
            user_msg += f"Barriers:{barriers_remaining}\n"

        return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]

    def build_thief_prompt(
        self, observation: str, valid_moves: list[str], history: list[str]
    ) -> list[dict]:
        sys_msg = (
            "Role: Thief on 5x5 grid. Strategy: Maximize distance from cop. Always flee! "
            'Output JSON only: {"action":"up|down|left|right|up-left|'
            'up-right|down-left|down-right","dialogue":"quip"}'
        )
        user_msg = (
            f"Obs:{observation}\nMoves:{valid_moves}\n"
            "Goal: Increase distance from cop (e.g. if cop north, go south. "
            "if north-east, go down-left).\n"
            f"History:{history}\n"
        )
        return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]

    def parse_response(self, resp_text: str, valid_moves: list[str]) -> tuple[str, str]:
        """Extract action and dialogue from LLM JSON response."""
        try:
            # Strip markdown code blocks if present
            clean = re.sub(r"```json\s*|\s*```", "", resp_text).strip()
            data = json.loads(clean)
            action = self.parse_direction(str(data.get("action", "")), valid_moves)
            dialogue = str(data.get("dialogue", ""))
            return action, dialogue
        except Exception:
            return self.parse_direction(resp_text, valid_moves), resp_text

    def parse_direction(self, text: str, valid_moves: list[str]) -> str:
        text = text.lower()
        for d in valid_moves:
            if d in text:
                return d
        return valid_moves[0] if valid_moves else "up"
