import os
import random

import numpy as np

from cop_thief.shared.config_loader import ConfigLoader


class QTable:
    def __init__(self, config: ConfigLoader):
        grid_size = config.get_grid_size()
        self.num_states = (grid_size[0] * grid_size[1]) ** 2
        rl_config = config.get_rl_config()
        self.num_actions = rl_config.get("num_actions", 8)

        self.learning_rate = rl_config["learning_rate"]
        self.discount_factor = rl_config["discount_factor"]
        self.epsilon = rl_config["epsilon"]

        self.table = np.zeros((self.num_states, self.num_actions))
        self.action_to_idx = {
            "up": 0, "down": 1, "left": 2, "right": 3,
            "up-left": 4, "up-right": 5, "down-left": 6, "down-right": 7
        }
        self.idx_to_action = {v: k for k, v in self.action_to_idx.items()}

    def encode_state(
        self, entity_pos: tuple[int, int], opponent_pos: tuple[int, int], grid_size: list[int]
    ) -> int:
        r, c = entity_pos
        op_r, op_c = opponent_pos
        cols = grid_size[1]

        entity_idx = r * cols + c
        opponent_idx = op_r * cols + op_c

        total_cells = grid_size[0] * grid_size[1]
        return entity_idx * total_cells + opponent_idx

    def get_q_value(self, state: int, action: str) -> float:
        a_idx = self.action_to_idx[action]
        return float(self.table[state, a_idx])

    def set_q_value(self, state: int, action: str, value: float) -> None:
        a_idx = self.action_to_idx[action]
        self.table[state, a_idx] = value

    def update_bellman(
        self, state: int, action: str, reward: float, next_state: int, done: bool
    ) -> None:
        a_idx = self.action_to_idx[action]
        current_q = self.table[state, a_idx]

        max_next_q = 0.0 if done else np.max(self.table[next_state])

        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.table[state, a_idx] = new_q

    def choose_action(self, state: int, valid_actions: list[str]) -> str:
        if not valid_actions:
            return "up"

        if random.random() < self.epsilon:
            return random.choice(valid_actions)

        best_action = valid_actions[0]
        best_q = self.get_q_value(state, best_action)

        for a in valid_actions[1:]:
            q = self.get_q_value(state, a)
            if q > best_q:
                best_q = q
                best_action = a

        return best_action

    def save(self, path: str = "results/q_table.npy") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.save(path, self.table)

    def load(self, path: str = "results/q_table.npy") -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Q-table file not found: {path}")
        loaded_table = np.load(path)
        if loaded_table.shape != (self.num_states, self.num_actions):
            expected = (self.num_states, self.num_actions)
            print(f"Warning: Shape {loaded_table.shape} doesn't match {expected}. Resetting.")
            self.reset()
        else:
            self.table = loaded_table

    def reset(self) -> None:
        self.table = np.zeros((self.num_states, self.num_actions))
