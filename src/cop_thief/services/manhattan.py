from cop_thief.services.entities import Entity
from cop_thief.services.grid import Grid
from cop_thief.services.move_validator import MoveValidator


class ManhattanHeuristic:
    def __init__(self, grid: Grid):
        self.grid = grid

    def get_distance(self, pos_a: tuple[int, int], pos_b: tuple[int, int]) -> int:
        return abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])

    def get_best_cop_move(self, cop: Entity, thief: Entity, validator: MoveValidator) -> str | None:
        moves = self.evaluate_all_moves(cop, thief, validator, minimize=True)
        if not moves:
            return self.handle_no_valid_moves(cop)
        return moves[0][0]

    def get_best_thief_move(
        self, thief: Entity, cop: Entity, validator: MoveValidator
    ) -> str | None:
        moves = self.evaluate_all_moves(thief, cop, validator, minimize=False)
        if not moves:
            return self.handle_no_valid_moves(thief)
        return moves[0][0]

    def evaluate_all_moves(
        self, entity: Entity, target: Entity, validator: MoveValidator, minimize: bool
    ) -> list[tuple[str, int]]:
        valid_dirs = validator.get_valid_moves(entity)
        if not valid_dirs:
            return []

        scored_moves = []
        for d in valid_dirs:
            dr, dc = validator._get_delta(d)
            new_pos = (entity.row + dr, entity.col + dc)
            dist = self.get_distance(new_pos, target.get_position())
            scored_moves.append((d, dist))

        scored_moves.sort(key=lambda x: x[1], reverse=not minimize)
        return scored_moves

    def handle_no_valid_moves(self, entity: Entity) -> None:
        return None
