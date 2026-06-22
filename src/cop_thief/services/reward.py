from cop_thief.services.game_state import GameState
from cop_thief.shared.config_loader import ConfigLoader


class RewardCalculator:
    def __init__(self, config: ConfigLoader):
        scoring = config.get_scoring()
        self.cop_win = scoring["cop_win"]
        self.thief_win = scoring["thief_win"]
        self.cop_loss = scoring["cop_loss"]
        self.thief_loss = scoring["thief_loss"]

    def calculate_cop_reward(self, game_state: GameState) -> float:
        if game_state.is_capture():
            return float(self.cop_win)
        if game_state.is_timeout():
            return float(-self.thief_win)
        return -1.0

    def calculate_thief_reward(self, game_state: GameState) -> float:
        if game_state.is_capture():
            return float(-self.cop_win)
        if game_state.is_timeout():
            return float(self.thief_win)
        return -1.0
