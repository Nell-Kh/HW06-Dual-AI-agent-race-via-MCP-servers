from cop_thief.services.cost_tracker import CostTracker
from cop_thief.services.orchestrator import Orchestrator
from cop_thief.services.partial_observer import PartialObserver
from cop_thief.services.q_table import QTable
from cop_thief.services.score_manager import ScoreManager
from cop_thief.services.transcript import TranscriptWriter
from cop_thief.shared.api_gatekeeper import ApiGatekeeper
from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.llm_client import LLMClient
from cop_thief.shared.secrets_manager import SecretsManager


class GameRunner:
    def __init__(self, config_path: str = "config/config.json"):
        self.config = ConfigLoader(config_path)
        self.config.load()
        self.secrets = SecretsManager()
        self.gatekeeper = ApiGatekeeper()
        self.llm_client = LLMClient(self.config, self.secrets)

        self.score_manager = ScoreManager(self.config)
        self.q_table = QTable(self.config)
        self.partial_observer = PartialObserver(self.config)
        self.cost_tracker = CostTracker(self.config)
        self.transcript_writer = TranscriptWriter(self.config)

        # We don't actually launch the MCP servers here because fastmcp starts on run().
        # In a real setup, we'd spawn them as subprocesses. For now we pass Mocks or None.
        self.cop_server = None
        self.thief_server = None

        self.orchestrator = Orchestrator(
            self.config,
            self.llm_client,
            self.cop_server,
            self.thief_server,
            self.score_manager,
            self.q_table,
            self.partial_observer,
            self.cost_tracker,
            self.transcript_writer,
        )

    def run(self) -> dict:
        results = self.orchestrator.run_game()
        self.cost_tracker.save_report()
        self.transcript_writer.save()
        return results

    def get_final_scores(self) -> dict:
        return self.score_manager.get_scores()
