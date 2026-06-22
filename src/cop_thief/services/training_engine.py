import json
import os

from cop_thief.services.game_state import GameState
from cop_thief.services.q_table import QTable
from cop_thief.shared.config_loader import ConfigLoader


class TrainingEngine:
    def __init__(self, config: ConfigLoader, q_table: QTable):
        self.config = config
        self.q_table = q_table
        try:
            train_config = config._config.get("training", {})
            self.num_episodes = train_config.get("num_episodes", 500)
            self.save_path = train_config.get("save_path", "results/q_table_trained.npy")
            self.log_path = train_config.get("log_path", "results/training_log.jsonl")
        except Exception:
            self.num_episodes = 500
            self.save_path = "results/q_table_trained.npy"
            self.log_path = "results/training_log.jsonl"
        self.logs = []

    def run_headless_games(self) -> None:
        os.makedirs(os.path.dirname(self.save_path) or ".", exist_ok=True)
        for ep in range(self.num_episodes):
            game = GameState(self.config)
            game.reset_for_sub_game()
            moves = 0
            while moves < self.config.get_max_moves():
                cop_pos = (game.cop.row, game.cop.col)
                thief_pos = (game.thief.row, game.thief.col)
                grid_size = [game.grid.rows, game.grid.cols]
                state_int = self.q_table.encode_state(cop_pos, thief_pos, grid_size)
                action = self.q_table.choose_action(
                    state=state_int, valid_actions=["up", "down", "left", "right"]
                )

                if action == "up" and game.cop.row > 0:
                    game.cop.move(game.cop.row - 1, game.cop.col)
                elif action == "down" and game.cop.row < game.grid.rows - 1:
                    game.cop.move(game.cop.row + 1, game.cop.col)
                elif action == "left" and game.cop.col > 0:
                    game.cop.move(game.cop.row, game.cop.col - 1)
                elif action == "right" and game.cop.col < game.grid.cols - 1:
                    game.cop.move(game.cop.row, game.cop.col + 1)

                new_state_int = self.q_table.encode_state(
                    (game.cop.row, game.cop.col), thief_pos, [game.grid.rows, game.grid.cols]
                )
                is_caught = game.cop.row == game.thief.row and game.cop.col == game.thief.col
                reward = 10 if is_caught else -1
                self.q_table.update_bellman(state_int, action, reward, new_state_int, is_caught)

                moves += 1
                if is_caught:
                    break

            self.logs.append({"episode": ep, "moves": moves})

        self.q_table.save(self.save_path)
        self.save_training_log()

    def save_training_log(self) -> None:
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            for log in self.logs:
                f.write(json.dumps(log) + "\n")
