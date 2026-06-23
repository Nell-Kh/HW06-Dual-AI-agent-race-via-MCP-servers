from fastmcp import FastMCP

from cop_thief.shared.config_loader import ConfigLoader


class CopMCPServer:
    def __init__(self, config: ConfigLoader):
        self.port = config.get_mcp_ports()["cop_server_port"]
        self.app = FastMCP("cop-server")

        self.state = {"pos": (0, 0), "barriers": 5}

        @self.app.tool()
        def move(direction: str) -> str:
            """Move the cop in a direction."""
            valid = [
                "up", "down", "left", "right",
                "up-left", "up-right", "down-left", "down-right"
            ]
            if direction not in valid:
                return "Invalid direction"
            return f"Cop moved {direction}"

        @self.app.tool()
        def place_barrier() -> str:
            """Place a barrier."""
            if self.state["barriers"] > 0:
                self.state["barriers"] -= 1
                return f"Barrier placed at {self.state['pos']}"
            return "No barriers remaining"

        @self.app.tool()
        def observe() -> str:
            """Observe the environment."""
            return (
                "You are in the upper-left area. The thief is 3 steps to your east. "
                f"You have {self.state['barriers']} barriers remaining."
            )

        @self.app.tool()
        def get_valid_moves() -> list[str]:
            """Get valid moves."""
            return ["up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"]

        # Store for testing
        self._observe = observe
        self._get_valid_moves = get_valid_moves

    def start(self) -> None:
        self.app.run(transport="sse", port=self.port)

    def stop(self) -> None:
        pass
