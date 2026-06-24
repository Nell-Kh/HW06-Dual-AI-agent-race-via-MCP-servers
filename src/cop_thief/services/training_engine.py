import json
import os
import random

from cop_thief.services.game_state import GameState
from cop_thief.services.manhattan import ManhattanHeuristic
from cop_thief.services.move_validator import MoveValidator
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

        initial_epsilon = self.q_table.epsilon
        min_epsilon = 0.05
        decay_rate = (initial_epsilon - min_epsilon) / max(1, self.num_episodes * 0.8)

        for ep in range(self.num_episodes):
            self.q_table.epsilon = max(min_epsilon, initial_epsilon - (ep * decay_rate))

            game = GameState(self.config)
            game.reset_for_sub_game()
            validator = MoveValidator(game.grid)
            heuristic = ManhattanHeuristic(game.grid)

            moves = 0
            while moves < self.config.get_max_moves():
                cop_pos = (game.cop.row, game.cop.col)
                thief_pos = (game.thief.row, game.thief.col)
                grid_size = [game.grid.rows, game.grid.cols]

                valid_cop_actions = validator.get_valid_moves(game.cop)
                if valid_cop_actions:
                    if random.random() < 0.5:
                        cop_action = heuristic.get_best_cop_move(game.cop, game.thief, validator)
                    else:
                        cop_action = random.choice(valid_cop_actions)
                    if cop_action:
                        dr, dc = validator._get_delta(cop_action)
                        game.cop.move(game.cop.row + dr, game.cop.col + dc)

                new_cop_pos = (game.cop.row, game.cop.col)
                
                if game.cop.row == game.thief.row and game.cop.col == game.thief.col:
                    moves += 1
                    break

                state_int = self.q_table.encode_state(new_cop_pos, thief_pos, grid_size)

                valid_actions = validator.get_valid_moves(game.thief)
                if not valid_actions:
                    break

                action = self.q_table.choose_action(
                    state=state_int, valid_actions=valid_actions
                )

                dr, dc = validator._get_delta(action)
                game.thief.move(game.thief.row + dr, game.thief.col + dc)

                new_thief_pos = (game.thief.row, game.thief.col)
                new_state_int = self.q_table.encode_state(
                    new_cop_pos, new_thief_pos, grid_size
                )

                is_caught = game.cop.row == game.thief.row and game.cop.col == game.thief.col

                if is_caught:
                    reward = 10.0
                else:
                    dist_before = heuristic.get_distance(new_cop_pos, thief_pos)
                    dist_after = heuristic.get_distance(new_cop_pos, new_thief_pos)
                    if dist_after < dist_before:
                        reward = 1.0
                    elif dist_after > dist_before:
                        reward = -2.0
                    else:
                        reward = -1.0

                self.q_table.update_bellman(state_int, action, reward, new_state_int, is_caught)

                moves += 1
                if is_caught:
                    break

            self.logs.append({"episode": ep, "moves": moves, "epsilon": self.q_table.epsilon})

        self.q_table.epsilon = initial_epsilon

        self.q_table.save(self.save_path)
        self.save_training_log()

    def save_training_log(self) -> None:
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            for log in self.logs:
                f.write(json.dumps(log) + "\n")
