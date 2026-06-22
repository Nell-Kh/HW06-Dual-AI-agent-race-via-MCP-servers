import random

from cop_thief.services.entities import Cop, Thief
from cop_thief.services.grid import Grid
from cop_thief.services.score_manager import ScoreManager
from cop_thief.shared.config_loader import ConfigLoader


class GameState:
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.grid = Grid(config)
        self.cop = Cop("cop", 0, 0, config)
        self.thief = Thief("thief", 0, 0)
        self.score_manager = ScoreManager(config)
        self.turn_count = 0
        self.max_moves = config.get_max_moves()

    def reset_for_sub_game(self) -> None:
        self.grid.reset()
        self.turn_count = 0
        rows, cols = self.config.get_grid_size()

        while True:
            cr, cc = random.randint(0, rows - 1), random.randint(0, cols - 1)
            tr, tc = random.randint(0, rows - 1), random.randint(0, cols - 1)
            if cr != tr or cc != tc:
                self.cop.set_position(cr, cc)
                self.thief.set_position(tr, tc)
                break

    def is_capture(self) -> bool:
        return self.cop.get_position() == self.thief.get_position()

    def is_timeout(self) -> bool:
        return self.turn_count >= self.max_moves

    def increment_turn(self) -> None:
        self.turn_count += 1

    def get_turn_count(self) -> int:
        return self.turn_count

    @property
    def thief_moves_first(self) -> bool:
        return True
