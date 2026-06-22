import json

import pytest

from cop_thief.services.entities import Cop, Thief
from cop_thief.services.game_state import GameState
from cop_thief.services.grid import Grid
from cop_thief.services.move_validator import MoveValidator
from cop_thief.services.score_manager import ScoreManager
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
        "llm": {"provider": "anthropic", "model": "test", "max_tokens": 1000, "temperature": 0.7},
        "mcp": {"cop_server_port": 8001, "thief_server_port": 8002, "host": "127.0.0.1"},
        "rl": {"learning_rate": 0.1, "discount_factor": 0.9, "epsilon": 0.2},
        "report": {"recipient": "x", "timezone": "y", "group_name": "z", "github_repo": "w"},
    }
    p = tmp_path / "config.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f)
    loader = ConfigLoader(str(p))
    loader.load()
    return loader


def test_grid_within_bounds_corners(mock_config):
    grid = Grid(mock_config)
    assert grid.is_within_bounds(0, 0) is True
    assert grid.is_within_bounds(0, 4) is True
    assert grid.is_within_bounds(4, 0) is True
    assert grid.is_within_bounds(4, 4) is True


def test_grid_outside_bounds(mock_config):
    grid = Grid(mock_config)
    assert grid.is_within_bounds(-1, 0) is False
    assert grid.is_within_bounds(0, -1) is False
    assert grid.is_within_bounds(5, 5) is False


def test_grid_place_barrier_success(mock_config):
    grid = Grid(mock_config)
    grid.place_barrier(2, 2)
    assert grid.is_barrier(2, 2) is True


def test_grid_place_barrier_out_of_bounds(mock_config):
    grid = Grid(mock_config)
    with pytest.raises(ValueError):
        grid.place_barrier(5, 5)


def test_grid_place_barrier_duplicate(mock_config):
    grid = Grid(mock_config)
    grid.place_barrier(1, 1)
    with pytest.raises(ValueError):
        grid.place_barrier(1, 1)


def test_grid_num_states_dynamic(mock_config):
    grid = Grid(mock_config)
    assert grid.get_num_states() == 25


def test_cop_place_barrier_decrements_count(mock_config):
    cop = Cop("cop", 0, 0, mock_config)
    grid = Grid(mock_config)
    assert cop.barriers_remaining == 5
    cop.place_barrier(grid)
    assert cop.barriers_remaining == 4
    assert grid.is_barrier(0, 0) is True


def test_cop_cannot_place_barrier_when_zero_remaining(mock_config):
    cop = Cop("cop", 0, 0, mock_config)
    grid = Grid(mock_config)
    for _ in range(5):
        cop.place_barrier(grid)
        cop.move(cop.row, cop.col + 1)
    with pytest.raises(ValueError):
        cop.place_barrier(grid)


def test_move_validator_valid_move(mock_config):
    grid = Grid(mock_config)
    val = MoveValidator(grid)
    thief = Thief("thief", 2, 2)
    assert val.is_valid_move(thief, "up") is True


def test_move_validator_blocked_by_barrier(mock_config):
    grid = Grid(mock_config)
    grid.place_barrier(1, 2)
    val = MoveValidator(grid)
    thief = Thief("thief", 2, 2)
    assert val.is_valid_move(thief, "up") is False


def test_move_validator_blocked_by_boundary(mock_config):
    grid = Grid(mock_config)
    val = MoveValidator(grid)
    thief = Thief("thief", 0, 2)
    assert val.is_valid_move(thief, "up") is False


def test_move_validator_get_valid_moves_corner(mock_config):
    grid = Grid(mock_config)
    val = MoveValidator(grid)
    thief = Thief("thief", 0, 0)
    moves = val.get_valid_moves(thief)
    assert sorted(moves) == ["down", "right"]


def test_score_manager_cop_win(mock_config):
    sm = ScoreManager(mock_config)
    sm.record_cop_win()
    scores = sm.get_scores()
    assert scores["cop"] == 20
    assert scores["thief"] == 5


def test_score_manager_thief_win(mock_config):
    sm = ScoreManager(mock_config)
    sm.record_thief_win()
    scores = sm.get_scores()
    assert scores["cop"] == 5
    assert scores["thief"] == 10


def test_score_manager_values_from_config(mock_config):
    sm = ScoreManager(mock_config)
    assert sm.cop_win_pts == 20


def test_game_state_capture_detection(mock_config):
    gs = GameState(mock_config)
    gs.cop.move(2, 2)
    gs.thief.move(2, 2)
    assert gs.is_capture() is True


def test_game_state_timeout_detection(mock_config):
    gs = GameState(mock_config)
    gs.turn_count = 25
    assert gs.is_timeout() is True


def test_game_state_thief_moves_first(mock_config):
    gs = GameState(mock_config)
    assert gs.thief_moves_first is True
