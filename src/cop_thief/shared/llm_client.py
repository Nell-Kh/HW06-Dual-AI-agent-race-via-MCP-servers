import openai

from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.prompt_builder import PromptBuilder
from cop_thief.shared.secrets_manager import SecretsManager


class LLMClient:
    def __init__(self, config: ConfigLoader, secrets: SecretsManager):
        self.client = openai.OpenAI(api_key=secrets.get_openai_key())
        llm_config = config.get_llm_config()
        self.model = llm_config["model"]
        self.max_tokens = llm_config["max_tokens"]
        self.temperature = llm_config["temperature"]
        self.config = config
        personas = config.get_config().get("personas", {})
        self.cop_persona = personas.get("cop", "You are Detective Marlowe, a relentless cop.")
        self.thief_persona = personas.get("thief", "You are The Shadow, a cunning thief.")
        self.prompt_builder = PromptBuilder(self.cop_persona, self.thief_persona)

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
            messages = self.prompt_builder.build_cop_prompt(
                observation, valid_moves, game_history
            )
        else:
            messages = self.prompt_builder.build_thief_prompt(
                observation, valid_moves, game_history
            )

        try:
            response = self.client.chat.completions.create(  # type: ignore
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            resp_text = response.choices[0].message.content or ""
            action, dialogue = self.prompt_builder.parse_response(resp_text, valid_moves)
            usage = response.usage
            pt = usage.prompt_tokens if usage else 0
            ct = usage.completion_tokens if usage else 0
        except Exception:
            action = valid_moves[0] if valid_moves else "up"
            dialogue = ""
            pt = 0
            ct = 0

        return {
            "action": action,
            "dialogue": dialogue,
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "model": self.model,
        }

    def generate_barrier_decision(
        self, cop_observation: str, valid_moves: list[str], barriers_remaining: int
    ) -> dict:
        if barriers_remaining <= 0:
            return self.generate_move("cop", cop_observation, valid_moves, [])

        persona = self.cop_persona
        sys_msg = (
            f"{persona} "
            "Respond with JSON containing 'action' (direction or 'place_barrier') and 'dialogue'."
        )
        user_msg = (
            f"Observation: {cop_observation}\n"
            f"Valid moves: {', '.join(valid_moves)}\n"
            f"Barriers remaining: {barriers_remaining}"
        )
        messages: list[dict] = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg},
        ]
        try:
            response = self.client.chat.completions.create(  # type: ignore
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            resp_text = (response.choices[0].message.content or "").lower()
            valid_with_barrier = valid_moves + ["place_barrier"]
            action, dialogue = self.prompt_builder.parse_response(resp_text, valid_with_barrier)
            return {
                "action": action,
                "dialogue": dialogue,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "model": response.model,
            }
        except Exception:
            return {
                "action": valid_moves[0] if valid_moves else "up",
                "dialogue": "Error",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "model": self.model,
            }
