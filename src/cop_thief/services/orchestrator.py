from cop_thief.services.cost_tracker import CostTracker
from cop_thief.services.game_state import GameState
from cop_thief.services.move_validator import MoveValidator
from cop_thief.services.partial_observer import PartialObserver
from cop_thief.services.q_table import QTable
from cop_thief.services.score_manager import ScoreManager
from cop_thief.services.training_engine import TrainingEngine
from cop_thief.services.transcript import TranscriptWriter
from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.llm_client import LLMClient


class Orchestrator:
    def __init__(
        self,
        config: ConfigLoader,
        llm_client: LLMClient,
        cop_server,
        thief_server,
        score_manager: ScoreManager,
        q_table: QTable,
        partial_observer: PartialObserver,
        cost_tracker: CostTracker,
        transcript_writer: TranscriptWriter,
    ):
        self.config = config
        self.llm_client = llm_client
        self.cop_server = cop_server
        self.thief_server = thief_server
        self.score_manager = score_manager
        self.q_table = q_table
        self.partial_observer = partial_observer
        self.cost_tracker = cost_tracker
        self.transcript_writer = transcript_writer
        self.barriers_remaining = config.get_max_barriers()

    def run_game(self) -> dict:
        trainer = TrainingEngine(self.config, self.q_table)
        trainer.run_headless_games()

        num_games = self.config.get_num_games()
        sub_game_results = []
        for i in range(1, num_games + 1):
            res = self.run_sub_game(i)
            sub_game_results.append(res)

        return {"sub_games": sub_game_results, "final_scores": self.score_manager.get_scores()}

    def run_sub_game(self, sub_game_number: int) -> dict:
        game = GameState(self.config)
        game.reset_for_sub_game()
        validator = MoveValidator(game.grid)
        self.barriers_remaining = self.config.get_max_barriers()
        moves, max_moves, winner = 0, self.config.get_max_moves(), "timeout"

        while moves < max_moves:
            for ag, ent, opp, srv in [
                ("thief", game.thief, game.cop, self.thief_server),
                ("cop", game.cop, game.thief, self.cop_server),
            ]:
                self.execute_turn(ag, ent, opp, srv, game, validator, sub_game_number, moves + 1)
                if game.cop.row == game.thief.row and game.cop.col == game.thief.col:
                    winner = "cop"
                    break
            if winner == "cop":
                break
            moves += 1

        if winner == "timeout":
            winner = "thief"

        self.score_manager.update_scores(winner)
        return self._build_sub_game_result(sub_game_number, winner, moves)

    def execute_turn(
        self,
        agent_name: str,
        entity,
        opponent,
        mcp_server,
        game: GameState,
        validator: MoveValidator,
        sub_game: int,
        turn: int,
    ) -> str:
        pos, opp_pos = (entity.row, entity.col), (opponent.row, opponent.col)
        obs = self.partial_observer.generate_description(agent_name, game.grid, pos, opp_pos)
        valid_moves = validator.get_valid_moves(entity)

        g_sz = [game.grid.rows, game.grid.cols]
        c_pos, t_pos = (game.cop.row, game.cop.col), (game.thief.row, game.thief.col)
        state_int_before = self.q_table.encode_state(c_pos, t_pos, g_sz)

        if agent_name == "cop":
            result = self.llm_client.generate_barrier_decision(
                obs, valid_moves, self.barriers_remaining
            )
        else:
            result = self.llm_client.generate_move(agent_name, obs, valid_moves, [])

        action = result["action"]
        self.cost_tracker.record_call(
            result["prompt_tokens"], result["completion_tokens"], result["model"]
        )
        self.transcript_writer.record_move(
            sub_game, turn, agent_name, obs, action, result["dialogue"]
        )

        if action == "place_barrier" and agent_name == "cop" and self.barriers_remaining > 0:
            self.barriers_remaining -= 1
            if game.cop.row > 0 and not game.grid.is_barrier(game.cop.row - 1, game.cop.col):
                game.grid.place_barrier(game.cop.row - 1, game.cop.col)
        else:
            dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}.get(
                action, (0, 0)
            )
            nr, nc = entity.row + dr, entity.col + dc
            if 0 <= nr < game.grid.rows and 0 <= nc < game.grid.cols:
                entity.move(nr, nc)

        c_pos, t_pos = (game.cop.row, game.cop.col), (game.thief.row, game.thief.col)
        caught = c_pos == t_pos
        state_int_after = self.q_table.encode_state(c_pos, t_pos, g_sz)
        self.q_table.update_bellman(
            state_int_before, action, 10 if caught else -1, state_int_after, caught
        )

        return action

    def _build_sub_game_result(self, sub_game_number: int, winner: str, moves: int) -> dict:
        sc = self.score_manager.get_scores()
        return {
            "sub_game_number": sub_game_number,
            "winner": winner,
            "num_moves": moves,
            "cop_score": sc["cop"],
            "thief_score": sc["thief"],
        }
