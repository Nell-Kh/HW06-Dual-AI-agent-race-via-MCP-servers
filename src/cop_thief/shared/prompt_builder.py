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
            "You are Detective Marlowe, a relentless cop on a 5x5 grid chasing a thief.\n"
            "STRATEGY: You MUST close the distance to the thief every turn.\n"
            "- If you detect the thief's direction, move toward them immediately.\n"
            "- Use barriers to block the thief's escape routes, not randomly.\n"
            "- NEVER move away from the thief's last known position.\n"
            "- You win by occupying the same cell as the thief.\n"
            'Respond with JSON: {"action": '
            '"up/down/left/right/up-left/up-right/down-left/down-right/place_barrier", '
            '"dialogue": "short quip"}'
        )
        user_msg = (
            f"You are at position described as: {observation}\n"
            f"Valid moves: {valid_moves}\n"
            f"GOAL: Move toward the thief. Choose the move that REDUCES distance to the thief.\n"
            "If the thief is north, go up. If east, go right. "
            "If south, go down. If west, go left. "
            "If north-east, go up-right. If south-west, go down-left.\n"
            f"Recent history: {history}\n"
        )
        if barriers_remaining > 0:
            user_msg += f"Barriers remaining: {barriers_remaining}\n"
        user_msg += "Respond with JSON only."

        return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]

    def build_thief_prompt(
        self, observation: str, valid_moves: list[str], history: list[str]
    ) -> list[dict]:
        sys_msg = (
            "You are The Shadow, a cunning thief on a 5x5 grid evading a cop.\n"
            "STRATEGY: You MUST maximize distance from the cop every turn.\n"
            "- NEVER move toward the cop \u2014 always flee.\n"
            "- If the cop is north, go south. If east, go west.\n"
            "- Use the full grid \u2014 move to corners and edges to maximize escape routes.\n"
            "- You win by surviving 25 moves without being caught.\n"
            "NEVER walk toward the cop. Survival is everything.\n"
            'Respond with JSON: {"action": '
            '"up/down/left/right/up-left/up-right/down-left/down-right", '
            '"dialogue": "witty quip"}'
        )
        user_msg = (
            f"You are at position: {observation}\n"
            f"Valid moves: {valid_moves}\n"
            f"GOAL: Move AWAY from the cop. Choose the move that INCREASES distance from the cop.\n"
            "If cop is north, go south. If east, go west. If south, go north. If west, go east. "
            "If north-east, go down-left to flee. If south-west, go up-right.\n"
            f"Recent history: {history}\n"
            "Respond with JSON only."
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
