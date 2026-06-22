from cop_thief.services.game_runner import GameRunner


class CopThiefSDK:
    def __init__(self, config_path: str = "config/config.json"):
        self.game_runner = GameRunner(config_path)

    def run_game(self) -> dict:
        return self.game_runner.run()

    def get_scores(self) -> dict:
        return self.game_runner.get_final_scores()
