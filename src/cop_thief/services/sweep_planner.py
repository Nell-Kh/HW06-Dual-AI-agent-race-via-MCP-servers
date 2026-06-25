class SweepPlanner:
    def __init__(self):
        self.state = 0

    def reset(self) -> None:
        self.state = 0

    def next_action(
        self,
        current_pos: tuple[int, int],
        valid_moves: list[str],
        barriers_remaining: int,
        opponent_pos: tuple[int, int] | None = None,
    ) -> str:
        if not valid_moves:
            return "up"

        if opponent_pos:
            r1, c1 = current_pos
            r2, c2 = opponent_pos
            if max(abs(r1 - r2), abs(c1 - c2)) <= 1 and (r1 != r2 or c1 != c2):
                best = valid_moves[0]
                best_dist = float("inf")
                deltas = {
                    "up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1),
                    "up-left": (-1, -1), "up-right": (-1, 1),
                    "down-left": (1, -1), "down-right": (1, 1),
                }
                for m in valid_moves:
                    dr, dc = deltas.get(m, (0, 0))
                    # Use Chebyshev distance for the 8-way movement
                    d = max(abs((r1 + dr) - r2), abs((c1 + dc) - c2))
                    if d < best_dist:
                        best_dist = d
                        best = m
                return best

        r, c = current_pos

        def chebyshev(p1, p2):
            return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

        r2, c2 = None, None
        if opponent_pos and chebyshev(current_pos, opponent_pos) <= 1:
            r2, c2 = opponent_pos

        import random

        # 1. Vision: Pounce!
        if r2 is not None:
            tr, tc = r2, c2
        else:
            # 2. Stochastic Patrol
            if (
                not hasattr(self, "patrol_target")
                or self.patrol_target is None
                or current_pos == self.patrol_target
            ):
                self.patrol_target = (random.randint(0, 4), random.randint(0, 4))
            tr, tc = self.patrol_target

            # 3. Chaotic Barriers
            if barriers_remaining > 0 and random.random() < 0.15:
                return "place_barrier"

        dir_r = "down" if tr > r else "up" if tr < r else ""
        dir_c = "right" if tc > c else "left" if tc < c else ""
        desired = dir_r + ("-" + dir_c if dir_r and dir_c else dir_c)

        if desired and desired in valid_moves:
            return desired
        if dir_r and dir_r in valid_moves:
            return dir_r
        if dir_c and dir_c in valid_moves:
            return dir_c

        # Blocked? Pick a new target if patrolling
        if r2 is None:
            self.patrol_target = None

        choices = valid_moves
        return random.choice(choices) if choices else (valid_moves[0] if valid_moves else "up")
