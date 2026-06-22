import openai

from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.secrets_manager import SecretsManager


class LLMClient:
    def __init__(self, config: ConfigLoader, secrets: SecretsManager):
        self.client = openai.OpenAI(api_key=secrets.get_openai_key())
        llm_config = config.get_llm_config()
        self.model = llm_config["model"]
        self.max_tokens = llm_config["max_tokens"]
        self.temperature = llm_config["temperature"]

    def _build_cop_prompt(
        self, observation: str, valid_moves: list[str], history: list[str]
    ) -> list[dict[str, str]]:
        try:
            persona = self.config._config.get("personas", {}).get("cop", "You are a cop.")
        except Exception:
            persona = "You are a cop."
        sys_msg = (
            f"{persona} Respond with JSON containing 'action' (direction) and 'dialogue' (quip)."
        )
        user_msg = (
            f"Observation: {observation}\n"
            f"Valid moves: {', '.join(valid_moves)}\n"
            f"History: {', '.join(history) if history else 'None'}"
        )
        return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]

    def _build_thief_prompt(
        self, observation: str, valid_moves: list[str], history: list[str]
    ) -> list[dict[str, str]]:
        try:
            persona = self.config._config.get("personas", {}).get("thief", "You are a thief.")
        except Exception:
            persona = "You are a thief."
        sys_msg = (
            f"{persona} Respond with JSON containing 'action' (direction) and 'dialogue' (quip)."
        )
        user_msg = (
            f"Observation: {observation}\n"
            f"Valid moves: {', '.join(valid_moves)}\n"
            f"History: {', '.join(history) if history else 'None'}"
        )
        return [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]

    def _parse_direction(self, response_text: str, valid_moves: list[str]) -> str:
        text = response_text.lower()
        for d in valid_moves:
            if d in text:
                return d
        return valid_moves[0] if valid_moves else "up"

    def generate_move(
        self, agent_name: str, observation: str, valid_moves: list[str], game_history: list[str]
    ) -> dict:
        if not valid_moves:
            return {
                "action": "up",
                "dialogue": "I am trapped!",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "model": self.model,
            }
        if agent_name == "cop":
            messages = self._build_cop_prompt(observation, valid_moves, game_history)
        else:
            messages = self._build_thief_prompt(observation, valid_moves, game_history)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            resp_text = response.choices[0].message.content or ""
            usage = response.usage
            pt = usage.prompt_tokens if usage else 0
            ct = usage.completion_tokens if usage else 0
        except Exception:
            resp_text = ""
            pt = 0
            ct = 0

        action = self._parse_direction(resp_text, valid_moves)
        return {
            "action": action,
            "dialogue": resp_text,
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "model": self.model,
        }

    def generate_barrier_decision(
        self, cop_observation: str, valid_moves: list[str], barriers_remaining: int
    ) -> dict:
        if barriers_remaining <= 0:
            return self.generate_move("cop", cop_observation, valid_moves, [])

        try:
            persona = self.config._config.get("personas", {}).get("cop", "You are a cop.")
        except Exception:
            persona = "You are a cop."
        sys_msg = (
            f"{persona} "
            "Respond with JSON containing 'action' (direction or 'place_barrier') and 'dialogue'."
        )
        user_msg = (
            f"Observation: {cop_observation}\n"
            f"Valid moves: {', '.join(valid_moves)}\n"
            f"Barriers remaining: {barriers_remaining}"
        )
        messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            resp_text = (response.choices[0].message.content or "").lower()
            usage = response.usage
            pt = usage.prompt_tokens if usage else 0
            ct = usage.completion_tokens if usage else 0
            if "place_barrier" in resp_text:
                action = "place_barrier"
            else:
                action = self._parse_direction(resp_text, valid_moves)
            return {
                "action": action,
                "dialogue": resp_text,
                "prompt_tokens": pt,
                "completion_tokens": ct,
                "model": self.model,
            }
        except Exception:
            return {
                "action": valid_moves[0] if valid_moves else "up",
                "dialogue": "Error",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "model": self.model,
            }
