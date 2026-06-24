class CornerPlanner:
    def __init__(self):
        self.target = None

    def reset(self) -> None:
        self.target = None

    def next_action(
        self,
        current_pos: tuple[int, int],
        valid_moves: list[str],
        opponent_pos: tuple[int, int] | None = None,
    ) -> str:
        r, c = current_pos
        if opponent_pos:
            r2, c2 = opponent_pos
            if max(abs(r - r2), abs(c - c2)) <= 2:
                best = valid_moves[0] if valid_moves else "up"
                best_dist = -1
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
                    d = abs((r + dr) - r2) + abs((c + dc) - c2)
                    if d > best_dist:
                        best_dist = d
                        best = m
                return best
        if self.target is None:
            corners = [(0, 0), (0, 4), (4, 0), (4, 4)]
            best_corner = corners[0]
            max_dist = -1
            for cr, cc in corners:
                dist = abs(cr - 0) + abs(cc - 2)
                if dist > max_dist:
                    max_dist = dist
                    best_corner = (cr, cc)
            self.target = best_corner

        tr, tc = self.target

        if (r, c) == self.target:
            # Stay in corner — pick the move with smallest Manhattan distance back to target
            best = valid_moves[0] if valid_moves else "up"
            best_dist = float("inf")
            deltas = {
                "up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1),
                "up-left": (-1, -1), "up-right": (-1, 1), "down-left": (1, -1), "down-right": (1, 1)
            }
            for m in valid_moves:
                dr, dc = deltas.get(m, (0, 0))
                d = abs((r + dr) - tr) + abs((c + dc) - tc)
                if d < best_dist:
                    best_dist = d
                    best = m
            return best
        dir_r = "down" if tr > r else "up" if tr < r else ""
        dir_c = "right" if tc > c else "left" if tc < c else ""
        desired = dir_r + ("-" + dir_c if dir_r and dir_c else dir_c)
        if not desired:
            # Already at target corner — pick any valid move that doesn't leave the corner,
            # or just stay by picking the first valid move (move validator prevents out-of-bounds)
            return valid_moves[0] if valid_moves else "up"

        if desired in valid_moves:
            return desired

        if dir_r and dir_r in valid_moves:
            return dir_r
        if dir_c and dir_c in valid_moves:
            return dir_c

        return valid_moves[0] if valid_moves else "up"
