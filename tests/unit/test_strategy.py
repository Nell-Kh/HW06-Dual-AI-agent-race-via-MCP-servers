import json

import pytest

from cop_thief.services.entities import Cop, Thief
from cop_thief.services.game_state import GameState
from cop_thief.services.grid import Grid
from cop_thief.services.manhattan import ManhattanHeuristic
from cop_thief.services.move_validator import MoveValidator
from cop_thief.services.q_table import QTable
from cop_thief.services.reward import RewardCalculator
from cop_thief.shared.config_loader import ConfigLoader


@pytest.fixture
def mock_config(tmp_path):
    data = {
        "version": "1.00",
        "grid_size": [5, 5],
        "max_moves": 25,
        "num_games": 6,
        "max_barriers": 5,
        "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
        "agents": {"cop_start": "random", "thief_start": "random"},
        "llm": {
            "provider": "openai", "model": "gpt-4o-mini", "max_tokens": 1000, "temperature": 0.7
        },
        "mcp": {"cop_server_port": 8001, "thief_server_port": 8002, "host": "127.0.0.1"},
        "rl": {"learning_rate": 0.1, "discount_factor": 0.9, "epsilon": 0.2},
        "report": {"recipient": "x", "timezone": "y", "group_name": "z", "github_repo": "w"}
    }
    p = tmp_path / "config.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f)
    loader = ConfigLoader(str(p))
    loader.load()
    return loader

def test_manhattan_distance_same_cell(mock_config):
    h = ManhattanHeuristic(Grid(mock_config))
    assert h.get_distance((2, 2), (2, 2)) == 0

def test_manhattan_distance_adjacent(mock_config):
    h = ManhattanHeuristic(Grid(mock_config))
    assert h.get_distance((2, 2), (2, 3)) == 1

def test_manhattan_distance_opposite_corners(mock_config):
    h = ManhattanHeuristic(Grid(mock_config))
    assert h.get_distance((0, 0), (4, 4)) == 8

def test_cop_best_move_moves_closer(mock_config):
    grid = Grid(mock_config)
    val = MoveValidator(grid)
    h = ManhattanHeuristic(grid)
    cop = Cop("cop", 2, 2, mock_config)
    thief = Thief("thief", 0, 2)
    assert h.get_best_cop_move(cop, thief, val) == "up"

def test_thief_best_move_moves_away(mock_config):
    grid = Grid(mock_config)
    val = MoveValidator(grid)
    h = ManhattanHeuristic(grid)
    thief = Thief("thief", 2, 2)
    cop = Cop("cop", 0, 2, mock_config)
    best_move = h.get_best_thief_move(thief, cop, val)
    assert best_move in ["down", "left", "right"]

def test_thief_trapped_returns_none(mock_config):
    grid = Grid(mock_config)
    grid.place_barrier(0, 1)
    grid.place_barrier(1, 0)
    val = MoveValidator(grid)
    h = ManhattanHeuristic(grid)
    thief = Thief("thief", 0, 0)
    cop = Cop("cop", 2, 2, mock_config)
    assert h.get_best_thief_move(thief, cop, val) is None

def test_qtable_init_num_states_dynamic(mock_config):
    q = QTable(mock_config)
    assert q.num_states == 25

def test_qtable_bellman_update(mock_config):
    q = QTable(mock_config)
    q.update_bellman(0, "up", 10.0, 1, False)
    assert q.get_q_value(0, "up") > 0.0

def test_qtable_bellman_done_state(mock_config):
    q = QTable(mock_config)
    q.set_q_value(1, "up", 5.0)
    q.update_bellman(0, "down", 10.0, 1, True)
    assert q.get_q_value(0, "down") == 1.0

def test_qtable_epsilon_greedy_explores(mock_config):
    q = QTable(mock_config)
    q.epsilon = 1.0
    action = q.choose_action(0, ["up", "down"])
    assert action in ["up", "down"]

def test_qtable_epsilon_greedy_exploits(mock_config):
    q = QTable(mock_config)
    q.epsilon = 0.0
    q.set_q_value(0, "up", 10.0)
    q.set_q_value(0, "down", 5.0)
    assert q.choose_action(0, ["up", "down"]) == "up"

def test_qtable_save_and_load(mock_config, tmp_path):
    q = QTable(mock_config)
    q.set_q_value(0, "up", 99.9)
    p = str(tmp_path / "q_table.npy")
    q.save(p)
    q2 = QTable(mock_config)
    q2.load(p)
    assert q2.get_q_value(0, "up") == 99.9

def test_reward_capture_cop_positive(mock_config):
    gs = GameState(mock_config)
    gs.cop.set_position(2, 2)
    gs.thief.set_position(2, 2)
    rc = RewardCalculator(mock_config)
    assert rc.calculate_cop_reward(gs) == 20.0
    assert rc.calculate_thief_reward(gs) == -20.0

def test_reward_timeout_thief_positive(mock_config):
    gs = GameState(mock_config)
    gs.thief.set_position(1, 1)
    gs.turn_count = 25
    rc = RewardCalculator(mock_config)
    assert rc.calculate_thief_reward(gs) == 10.0
    assert rc.calculate_cop_reward(gs) == -10.0

def test_reward_step_negative(mock_config):
    gs = GameState(mock_config)
    gs.thief.set_position(1, 1)
    rc = RewardCalculator(mock_config)
    assert rc.calculate_cop_reward(gs) == -1.0
    assert rc.calculate_thief_reward(gs) == -1.0
