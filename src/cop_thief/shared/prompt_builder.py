import json
import re


class PromptBuilder:
    def __init__(self, cop_persona: str, thief_persona: str):
        self.cop_persona = cop_persona
        self.thief_persona = thief_persona

    def build_cop_prompt(
        self, observation: str, valid_moves: list[str], history: list[str]
    ) -> list[dict]:
        persona = self.cop_persona
        sys_msg = (
            f"{persona} Respond with JSON containing 'action' (direction) and 'dialogue' (quip)."
        )
        user_msg = (
            f"Observation: {observation}\n"
            f"Valid moves: {', '.join(valid_moves)}\n"
            f"History: {', '.join(history) if history else 'None'}"
        )
        return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]

    def build_thief_prompt(
        self, observation: str, valid_moves: list[str], history: list[str]
    ) -> list[dict]:
        persona = self.thief_persona
        sys_msg = (
            f"{persona} Respond with JSON containing 'action' (direction) and 'dialogue' (quip)."
        )
        user_msg = (
            f"Observation: {observation}\n"
            f"Valid moves: {', '.join(valid_moves)}\n"
            f"History: {', '.join(history) if history else 'None'}"
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
