from src.cop_thief.services.entities import Entity
from src.cop_thief.services.grid import Grid


class MoveValidator:
    def __init__(self, grid: Grid):
        self.grid = grid

    def is_valid_move(self, entity: Entity, direction: str) -> bool:
        dr, dc = self._get_delta(direction)
        new_row = entity.row + dr
        new_col = entity.col + dc

        if not self.grid.is_within_bounds(new_row, new_col):
            return False
        return not self.grid.is_barrier(new_row, new_col)

    def get_valid_moves(self, entity: Entity) -> list[str]:
        directions = ["up", "down", "left", "right"]
        return [d for d in directions if self.is_valid_move(entity, d)]

    def apply_move(self, entity: Entity, direction: str) -> None:
        if not self.is_valid_move(entity, direction):
            raise ValueError("Invalid move")
        dr, dc = self._get_delta(direction)
        entity.set_position(entity.row + dr, entity.col + dc)

    def _get_delta(self, direction: str) -> tuple[int, int]:
        deltas = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        if direction not in deltas:
            raise ValueError("Invalid direction")
        return deltas[direction]
