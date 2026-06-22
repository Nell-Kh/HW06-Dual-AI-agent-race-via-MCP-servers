from src.cop_thief.services.grid import Grid
from src.cop_thief.shared.config_loader import ConfigLoader


class Entity:
    def __init__(self, name: str, row: int, col: int):
        self.name = name
        self.row = row
        self.col = col

    def get_position(self) -> tuple[int, int]:
        return (self.row, self.col)

    def set_position(self, row: int, col: int) -> None:
        self.row = row
        self.col = col

class Cop(Entity):
    def __init__(self, name: str, row: int, col: int, config: ConfigLoader):
        super().__init__(name, row, col)
        self._max_barriers = config.get_max_barriers()
        self._barriers_used = 0

    @property
    def barriers_remaining(self) -> int:
        return self._max_barriers - self._barriers_used

    def can_place_barrier(self) -> bool:
        return self.barriers_remaining > 0

    def place_barrier(self, grid: Grid) -> None:
        if not self.can_place_barrier():
            raise ValueError("No barriers remaining")
        grid.place_barrier(self.row, self.col)
        self._barriers_used += 1

class Thief(Entity):
    def __init__(self, name: str, row: int, col: int):
        super().__init__(name, row, col)
