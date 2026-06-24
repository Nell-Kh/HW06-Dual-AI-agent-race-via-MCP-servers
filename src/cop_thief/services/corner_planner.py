class CornerPlanner:
    def __init__(self):
        self.target = None

    def reset(self) -> None:
        self.target = None

    def next_action(self, current_pos: tuple[int, int], valid_moves: list[str]) -> str:
        r, c = current_pos
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

        dir_r = "down" if tr > r else "up" if tr < r else ""
        dir_c = "right" if tc > c else "left" if tc < c else ""
        desired = dir_r + ("-" + dir_c if dir_r and dir_c else dir_c)
        if not desired:
            desired = valid_moves[0] if valid_moves else "up"

        if desired in valid_moves:
            return desired

        if dir_r and dir_r in valid_moves:
            return dir_r
        if dir_c and dir_c in valid_moves:
            return dir_c

        return valid_moves[0] if valid_moves else "up"
