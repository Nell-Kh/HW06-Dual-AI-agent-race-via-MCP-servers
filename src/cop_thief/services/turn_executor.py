import contextlib
import re

from cop_thief.services.cost_tracker import CostTracker
from cop_thief.services.game_state import GameState
from cop_thief.services.html_replay import HTMLReplay
from cop_thief.services.move_validator import MoveValidator
from cop_thief.services.partial_observer import PartialObserver
from cop_thief.services.q_table import QTable
from cop_thief.services.transcript import TranscriptWriter
from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.llm_client import LLMClient


class TurnExecutor:
    def __init__(
        self,
        llm_client: LLMClient,
        q_table: QTable,
        partial_observer: PartialObserver,
        cost_tracker: CostTracker,
        transcript_writer: TranscriptWriter,
        html_replay: HTMLReplay,
        config: ConfigLoader,
    ):
        self.llm_client = llm_client
        self.q_table = q_table
        self.partial_observer = partial_observer
        self.cost_tracker = cost_tracker
        self.transcript_writer = transcript_writer
        self.html_replay = html_replay
        self.config = config

        self.reset()

    def reset(self):
        self.barriers_remaining = self.config.get_max_barriers()
        self.cop_history = []
        self.thief_history = []
        self.last_dialogue = {"cop": "", "thief": ""}
        self.last_seen = {"cop": None, "thief": None}

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
        obs, g_sz, state_int_before, result = self._decide_action(
            agent_name, entity, opponent, game, validator
        )
        action = result["action"]

        self._record_turn(sub_game, turn, agent_name, obs, action, result, game)
        self._apply_action(action, agent_name, entity, game, validator)
        self._update_learning(action, state_int_before, game, g_sz)
        self._update_history(agent_name, action, obs, result, turn)

        return action

    def _decide_action(self, agent_name, entity, opponent, game, validator):
        pos, opp_pos = (entity.row, entity.col), (opponent.row, opponent.col)
        obs = self.partial_observer.generate_description(agent_name, game.grid, pos, opp_pos)
        self._update_belief_state(agent_name, obs)
        valid_moves = validator.get_valid_moves(entity)

        g_sz = [game.grid.rows, game.grid.cols]
        c_pos, t_pos = (game.cop.row, game.cop.col), (game.thief.row, game.thief.col)
        state_int_before = self.q_table.encode_state(c_pos, t_pos, g_sz)

        history = self.cop_history if agent_name == "cop" else self.thief_history
        ls = self.last_seen[agent_name]
        opp_msg = self.last_dialogue["thief" if agent_name == "cop" else "cop"]

        if agent_name == "cop":
            result = self.llm_client.generate_barrier_decision(
                obs, valid_moves, self.barriers_remaining, history, ls, opp_msg
            )
        else:
            result = self.llm_client.generate_move(
                agent_name, obs, valid_moves, history, ls, opp_msg
            )

        return obs, g_sz, state_int_before, result

    def _update_belief_state(self, agent_name, obs):
        if "You see the opponent" in obs and (m := re.search(r"(\d+) steps ([a-z-]+)", obs)):
            self.last_seen[agent_name] = {
                "direction": m.group(2), "steps": int(m.group(1)), "turns_since": 0
            }
        elif "No sign" in obs and self.last_seen[agent_name]:
            self.last_seen[agent_name]["turns_since"] += 1

    def _record_turn(self, sub_game, turn, agent_name, obs, action, result, game):
        pt, ct, mod = result["prompt_tokens"], result["completion_tokens"], result["model"]
        self.cost_tracker.record_call(pt, ct, mod)
        self.transcript_writer.record_move(
            sub_game, turn, agent_name, obs, action, result["dialogue"]
        )
        c_p, t_p = (game.cop.row, game.cop.col), (game.thief.row, game.thief.col)
        bars, dlg = game.grid.get_barriers(), result["dialogue"]
        self.html_replay.add_frame(sub_game, turn, agent_name, c_p, t_p, bars, action, dlg)

    def _apply_action(self, action, agent_name, entity, game, validator):
        if action == "place_barrier" and agent_name == "cop" and self.barriers_remaining > 0:
            self.barriers_remaining -= 1
            row, col = game.cop.row, game.cop.col
            if not game.grid.is_barrier(row, col):
                game.grid.place_barrier(row, col)
        elif action != "place_barrier":
            with contextlib.suppress(ValueError):
                validator.apply_move(entity, action)

    def _update_learning(self, action, state_int_before, game, g_sz):
        c_pos, t_pos = (game.cop.row, game.cop.col), (game.thief.row, game.thief.col)
        caught = c_pos == t_pos
        state_int_after = self.q_table.encode_state(c_pos, t_pos, g_sz)
        # Only update Q-table for movement actions, not barrier placement
        if action in (
            "up", "down", "left", "right",
            "up-left", "up-right", "down-left", "down-right"
        ):
            self.q_table.update_bellman(
                state_int_before, action, 10 if caught else -1, state_int_after, caught
            )

    def _update_history(self, agent_name, action, obs, result, turn):
        opponent_name = "thief" if agent_name == "cop" else "cop"
        opp_msg = self.last_dialogue.get(opponent_name, "")
        entry = f"T{turn}: I moved {action} | saw {obs} | opponent said: '{opp_msg}'"

        if agent_name == "cop":
            self.cop_history.append(entry)
            if len(self.cop_history) > 4:
                self.cop_history.pop(0)
            self.last_dialogue["cop"] = result["dialogue"]
        else:
            self.thief_history.append(entry)
            if len(self.thief_history) > 4:
                self.thief_history.pop(0)
            self.last_dialogue["thief"] = result["dialogue"]
