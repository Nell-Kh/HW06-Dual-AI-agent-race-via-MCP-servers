from cop_thief.services.grid import Grid
from cop_thief.shared.config_loader import ConfigLoader


class PartialObserver:
    def __init__(self, config: ConfigLoader):
        try:
            self.radius = int(config._config.get("vision_radius", 2))
        except Exception:
            self.radius = 2

    def get_visible_state(self, grid: Grid, agent_pos: tuple[int, int]) -> dict:
        visible = {}
        for r in range(grid.rows):
            for c in range(grid.cols):
                if abs(r - agent_pos[0]) <= self.radius and abs(c - agent_pos[1]) <= self.radius:
                    visible[(r, c)] = grid.state[r][c]
                else:
                    visible[(r, c)] = "unknown"
        return visible

    def generate_description(
        self, agent_name: str, grid: Grid, agent_pos: tuple[int, int], opponent_pos: tuple[int, int]
    ) -> str:
        desc = ["You are at center."]
        r1, c1 = agent_pos
        r2, c2 = opponent_pos

        dist_r = abs(r1 - r2)
        dist_c = abs(c1 - c2)

        if dist_r <= self.radius and dist_c <= self.radius:
            steps = max(dist_r, dist_c)
            dir_r = "south" if r2 > r1 else "north" if r2 < r1 else ""
            dir_c = "east" if c2 > c1 else "west" if c2 < c1 else ""
            direction = dir_r + ("-" + dir_c if dir_r and dir_c else dir_c)
            msg = f"You see the opponent {steps} steps {direction} from you."
            desc.append(msg)
        else:
            desc.append("No sign of the opponent within your view.")

        barriers = []
        for r in range(max(0, r1 - self.radius), min(grid.rows, r1 + self.radius + 1)):
            for c in range(max(0, c1 - self.radius), min(grid.cols, c1 + self.radius + 1)):
                if grid.is_barrier(r, c):
                    bdir_r = "south" if r > r1 else "north" if r < r1 else ""
                    bdir_c = "east" if c > c1 else "west" if c < c1 else ""
                    bdirection = bdir_r + ("-" + bdir_c if bdir_r and bdir_c else bdir_c)
                    if bdirection:
                        barriers.append(f"There is a barrier to your {bdirection}.")
        if barriers:
            desc.extend(barriers)

        return " ".join(desc)
