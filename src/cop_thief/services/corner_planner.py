class CornerPlanner:
    def __init__(self):
        pass

    def reset(self) -> None:
        pass

    def next_action(
        self,
        current_pos: tuple[int, int],
        valid_moves: list[str],
        opponent_pos: tuple[int, int] | None = None,
    ) -> str:
        if not valid_moves:
            return "up"

        r, c = current_pos
        center = (2, 2)

        deltas = {
            "up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1),
            "up-left": (-1, -1), "up-right": (-1, 1), "down-left": (1, -1), "down-right": (1, 1)
        }

        def get_next_pos(move):
            dr, dc = deltas.get(move, (0, 0))
            return (r + dr, c + dc)

        def chebyshev(p1, p2):
            return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

        if opponent_pos:
            r2, c2 = opponent_pos
            if chebyshev(current_pos, opponent_pos) <= 2:
                best_dist = -1
                for m in valid_moves:
                    np_pos = get_next_pos(m)
                    d = chebyshev(np_pos, opponent_pos)
                    if d > best_dist:
                        best_dist = d

                if best_dist >= 2:
                    safe_moves = [
                        m for m in valid_moves
                        if chebyshev(get_next_pos(m), opponent_pos) >= 2
                    ]
                else:
                    safe_moves = [
                        m for m in valid_moves
                        if chebyshev(get_next_pos(m), opponent_pos) == best_dist
                    ]

                # Ghost strategy: move toward the opposite side of the board from the Cop
                ghost_target = (4 - r2, 4 - c2)
                min_ghost_dist = float('inf')
                best_moves = []
                for m in safe_moves:
                    np_pos = get_next_pos(m)
                    g_dist = abs(np_pos[0] - ghost_target[0]) + abs(np_pos[1] - ghost_target[1])
                    if g_dist < min_ghost_dist:
                        min_ghost_dist = g_dist
                        best_moves = [m]
                    elif g_dist == min_ghost_dist:
                        best_moves.append(m)
                import random
                return random.choice(best_moves) if best_moves else "up"

        import random
        min_center_dist = float('inf')
        best_moves = []
        for m in valid_moves:
            np_pos = get_next_pos(m)
            c_dist = abs(np_pos[0] - center[0]) + abs(np_pos[1] - center[1])
            if c_dist < min_center_dist:
                min_center_dist = c_dist
                best_moves = [m]
            elif c_dist == min_center_dist:
                best_moves.append(m)
        fallback = valid_moves[0] if valid_moves else "up"
        return random.choice(best_moves) if best_moves else fallback
