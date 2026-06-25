import json
import re


class PromptBuilder:
    def __init__(self, cop_persona: str, thief_persona: str):
        self.cop_persona = cop_persona
        self.thief_persona = thief_persona

    def _build_belief_block(self, agent_role: str, last_seen: dict | None, opp_msg: str) -> str:
        if last_seen is None:
            if agent_role == "cop":
                return (
                    "SEARCH. You haven't spotted the thief. "
                    "Sweep toward the center to maximize detection."
                )
            return "SEARCH. Cop not seen. Move toward an edge/corner to stay hidden."

        ts, st, dr = last_seen["turns_since"], last_seen["steps"], last_seen["direction"]
        if ts in (1, 2):
            act = "CLOSE distance" if agent_role == "cop" else "WIDEN distance"
            return (
                f"You last saw the opponent {st} steps {dr}, {ts} turn(s) ago — still close, "
                f"within ~{ts} cells. They said: '{opp_msg}'. Move decisively to {act}."
            )
        if ts in (3, 4):
            act = "toward" if agent_role == "cop" else "away from"
            return (
                f"Last saw opponent {st} steps {dr}, {ts} turns ago — could be several cells "
                f"away now. Move generally {act} that area without over-committing. "
                f"They said: '{opp_msg}'."
            )

        act = "sweep toward center." if agent_role == "cop" else "head for farthest corner."
        return f"Last sighting ({ts} turns ago) is unreliable. {act}"

    def build_cop_prompt(
        self,
        observation: str,
        valid_moves: list[str],
        history: list[str],
        barriers_remaining: int = 0,
        last_seen: dict | None = None,
        opponent_message: str = "",
    ) -> list[dict]:
        sys_msg = (
            "Role: Cop on 5x5 grid. Strategy: Close distance to thief. Block escape routes. "
            'Output JSON only: {"action":"up|down|left|right|up-left|up-right|'
            'down-left|down-right|place_barrier","dialogue":"write a highly contextual, '
            'meaningful, and dramatic sentence addressing the thief based on what you see '
            'or hear. React specifically to the opponent\'s last message!"}'
        )
        user_msg = (
            f"Obs:{observation}\nMoves:{valid_moves}\n"
            f"Goal: Reduce distance to thief (e.g. if north go up, north-east go up-right).\n"
        )
        if "No sign" in observation:
            bb = self._build_belief_block("cop", last_seen, opponent_message)
            user_msg += f"Belief: {bb}\n"
        user_msg += f"History:{history}\n"
        if opponent_message:
            user_msg += f"Opponent Message: '{opponent_message}'\n"
        if barriers_remaining > 0:
            user_msg += f"Barriers:{barriers_remaining}\n"

        return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]

    def build_thief_prompt(
        self,
        observation: str,
        valid_moves: list[str],
        history: list[str],
        last_seen: dict | None = None,
        opponent_message: str = "",
    ) -> list[dict]:
        sys_msg = (
            "Role: Thief on 5x5 grid. Strategy: Maximize distance from cop. Always flee! "
            'Output JSON only: {"action":"up|down|left|right|up-left|'
            'up-right|down-left|down-right","dialogue":"write a highly contextual, '
            'meaningful, and dramatic sentence taunting or addressing the cop based on what '
            'you see or hear. React specifically to the opponent\'s last message!"}'
        )
        user_msg = (
            f"Obs:{observation}\nMoves:{valid_moves}\n"
            "Goal: Increase distance from cop (e.g. if cop north, go south. "
            "if north-east, go down-left).\n"
        )
        if "No sign" in observation:
            bb = self._build_belief_block("thief", last_seen, opponent_message)
            user_msg += f"Belief: {bb}\n"
        user_msg += f"History:{history}\n"
        if opponent_message:
            user_msg += f"Opponent Message: '{opponent_message}'\n"
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
