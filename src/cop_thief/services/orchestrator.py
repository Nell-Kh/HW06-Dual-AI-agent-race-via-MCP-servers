from cop_thief.services.cost_tracker import CostTracker
from cop_thief.services.game_state import GameState
from cop_thief.services.html_replay import HTMLReplay
from cop_thief.services.move_validator import MoveValidator
from cop_thief.services.partial_observer import PartialObserver
from cop_thief.services.q_table import QTable
from cop_thief.services.score_manager import ScoreManager
from cop_thief.services.training_engine import TrainingEngine
from cop_thief.services.transcript import TranscriptWriter
from cop_thief.services.turn_executor import TurnExecutor
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
        html_replay: HTMLReplay,
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
        self.html_replay = html_replay

        self.turn_executor = TurnExecutor(
            llm_client=llm_client,
            q_table=q_table,
            partial_observer=partial_observer,
            cost_tracker=cost_tracker,
            transcript_writer=transcript_writer,
            html_replay=html_replay,
            config=config,
            use_sweep_cop=self.config.get_config().get("use_sweep_cop", True),
        )

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
        self.turn_executor.reset()
        moves, max_moves, winner = 0, self.config.get_max_moves(), "timeout"

        while moves < max_moves:
            moves += 1
            for ag, ent, opp, srv in [
                ("thief", game.thief, game.cop, self.thief_server),
                ("cop", game.cop, game.thief, self.cop_server),
            ]:
                self.turn_executor.execute_turn(
                    ag, ent, opp, srv, game, validator, sub_game_number, moves
                )
                if game.cop.row == game.thief.row and game.cop.col == game.thief.col:
                    winner = "cop"
                    self.html_replay.add_frame(
                        sub_game=sub_game_number,
                        turn=moves,
                        agent="System",
                        cop_pos=(game.cop.row, game.cop.col),
                        thief_pos=(game.thief.row, game.thief.col),
                        barriers=game.grid.get_barriers(),
                        action="game_over",
                        dialogue="Busted! The Cop caught the Thief!",
                    )
                    break
            if winner == "cop":
                break

        if winner == "timeout":
            winner = "thief"

        if winner == "cop":
            self.score_manager.record_cop_win()
        else:
            self.score_manager.record_thief_win()
        return self._build_sub_game_result(sub_game_number, winner, moves)

    def _build_sub_game_result(self, sub_game_number: int, winner: str, moves: int) -> dict:
        scoring = self.config.get_config().get("scoring", {})
        if winner == "cop":
            cop_score = scoring.get("cop_win", 20)
            thief_score = scoring.get("thief_loss", 5)
        else:
            cop_score = scoring.get("cop_loss", 5)
            thief_score = scoring.get("thief_win", 10)

        return {
            "sub_game_number": sub_game_number,
            "winner": winner,
            "num_moves": moves,
            "cop_score": cop_score,
            "thief_score": thief_score,
        }
