from src.cop_thief.shared.config_loader import ConfigLoader


class Grid:
    def __init__(self, config: ConfigLoader):
        self.rows, self.cols = config.get_grid_size()
        self.state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def place_barrier(self, row: int, col: int) -> None:
        if not self.is_within_bounds(row, col):
            raise ValueError("Out of bounds")
        if self.state[row][col] == 1:
            raise ValueError("Already a barrier")
        self.state[row][col] = 1

    def is_barrier(self, row: int, col: int) -> bool:
        if not self.is_within_bounds(row, col):
            return False
        return self.state[row][col] == 1

    def get_num_states(self) -> int:
        return self.rows * self.cols

    def reset(self) -> None:
        self.state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def to_display_string(self) -> str:
        lines = []
        for r in range(self.rows):
            row_str = " ".join(["X" if self.state[r][c] == 1 else "." for c in range(self.cols)])
            lines.append(row_str)
        return "\n".join(lines)
