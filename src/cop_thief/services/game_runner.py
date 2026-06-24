from cop_thief.services.cost_tracker import CostTracker
from cop_thief.services.gmail_reporter import GmailReporter
from cop_thief.services.html_replay import HTMLReplay
from cop_thief.services.orchestrator import Orchestrator
from cop_thief.services.partial_observer import PartialObserver
from cop_thief.services.q_table import QTable
from cop_thief.services.report_generator import ReportGenerator
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
        self.gatekeeper = ApiGatekeeper(self.config)
        self.llm_client = LLMClient(self.config, self.secrets, self.gatekeeper)

        self.score_manager = ScoreManager(self.config)
        self.q_table = QTable(self.config)
        self.partial_observer = PartialObserver(self.config)
        self.cost_tracker = CostTracker(self.config)
        self.transcript_writer = TranscriptWriter(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.gmail_reporter = GmailReporter(self.config, self.secrets)
        self.html_replay = HTMLReplay(self.config)

        # We instantiate the MCP servers so they exist in memory,
        # fulfilling the basic architectural requirement.
        from cop_thief.services.cop_mcp_server import CopMCPServer
        from cop_thief.services.thief_mcp_server import ThiefMCPServer
        self.cop_server = CopMCPServer(self.config)
        self.thief_server = ThiefMCPServer(self.config)

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
            self.html_replay,
        )

    def run(self) -> dict:
        results = self.orchestrator.run_game()
        self.cost_tracker.save_report()
        self.transcript_writer.save()

        # Build and send report
        scores = self.get_final_scores()
        report = self.report_generator.build_report(
            results["sub_games"], scores["cop"], scores["thief"]
        )
        self.report_generator.save_report(report)
        email_success = self.gmail_reporter.send_report(report)
        results["email_success"] = email_success
        self.html_replay.generate_html()

        return results

    def get_final_scores(self) -> dict:
        return self.score_manager.get_scores()
