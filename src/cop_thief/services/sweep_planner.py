class SweepPlanner:
    def __init__(self):
        self.step = 0
        self.plan = [
            "place_barrier",
            "down", "place_barrier",
            "down", "place_barrier",
            "down",
            "right",
            "up", "up",
            "down", "down",
            "left", "left",
            "up", "up",
        ]

    def reset(self) -> None:
        self.step = 0

    def next_action(
        self,
        current_pos: tuple[int, int],
        valid_moves: list[str],
        barriers_remaining: int,
        opponent_pos: tuple[int, int] | None = None,
    ) -> str:
        if opponent_pos:
            r1, c1 = current_pos
            r2, c2 = opponent_pos
            if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and (r1 != r2 or c1 != c2):
                dir_r = "down" if r2 > r1 else "up" if r2 < r1 else ""
                dir_c = "right" if c2 > c1 else "left" if c2 < c1 else ""
                desired = dir_r + ("-" + dir_c if dir_r and dir_c else dir_c)
                if desired in valid_moves:
                    return desired

        if self.step >= len(self.plan):
            return valid_moves[0] if valid_moves else "up"

        action = self.plan[self.step]
        self.step += 1

        if action == "place_barrier":
            if barriers_remaining > 0:
                return "place_barrier"
            else:
                return valid_moves[0] if valid_moves else "up"

        if action in valid_moves:
            return action
        return valid_moves[0] if valid_moves else "up"
