from cop_thief.shared.config_loader import ConfigLoader


class ScoreManager:
    def __init__(self, config: ConfigLoader):
        scoring = config.get_scoring()
        self.cop_win_pts = scoring["cop_win"]
        self.thief_win_pts = scoring["thief_win"]
        self.cop_loss_pts = scoring["cop_loss"]
        self.thief_loss_pts = scoring["thief_loss"]
        self.cop_score = 0
        self.thief_score = 0
        self.history: list[dict[str, str]] = []

    def record_cop_win(self) -> None:
        self.cop_score += self.cop_win_pts
        self.thief_score += self.cop_loss_pts
        self.history.append({"winner": "cop"})

    def record_thief_win(self) -> None:
        self.thief_score += self.thief_win_pts
        self.cop_score += self.thief_loss_pts
        self.history.append({"winner": "thief"})

    def get_scores(self) -> dict[str, int]:
        return {"cop": self.cop_score, "thief": self.thief_score}

    def reset_game_scores(self) -> None:
        self.cop_score = 0
        self.thief_score = 0
        self.history = []

    def get_sub_game_history(self) -> list[dict[str, str]]:
        return self.history
