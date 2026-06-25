class WallBuilder:
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
            if max(abs(r1 - r2), abs(c1 - c2)) <= 1 and (r1 != r2 or c1 != c2):
                best = valid_moves[0] if valid_moves else "up"
                best_dist = float("inf")
                deltas = {
                    "up": (-1, 0),
                    "down": (1, 0),
                    "left": (0, -1),
                    "right": (0, 1),
                    "up-left": (-1, -1),
                    "up-right": (-1, 1),
                    "down-left": (1, -1),
                    "down-right": (1, 1),
                }
                for m in valid_moves:
                    dr, dc = deltas.get(m, (0, 0))
                    d = abs((r1 + dr) - r2) + abs((c1 + dc) - c2)
                    if d < best_dist:
                        best_dist = d
                        best = m
                return best

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
