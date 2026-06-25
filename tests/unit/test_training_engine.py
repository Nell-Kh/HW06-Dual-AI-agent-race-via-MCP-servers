from unittest.mock import MagicMock, patch

import pytest

from cop_thief.services.q_table import QTable
from cop_thief.services.training_engine import TrainingEngine
from cop_thief.shared.config_loader import ConfigLoader


@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigLoader)
    config._config = {
        "training": {"num_episodes": 2, "save_path": "test_q.npy", "log_path": "test_log.jsonl"}
    }
    config.get_max_moves.return_value = 5
    config.get_grid_size.return_value = [5, 5]
    config.get_max_barriers.return_value = 5
    config.get_scoring.return_value = {"cop_win": 1, "thief_win": 1, "cop_loss": 1, "thief_loss": 1}
    return config


def test_training_engine_init(mock_config):
    q_table = MagicMock(spec=QTable)
    engine = TrainingEngine(mock_config, q_table)
    assert engine.num_episodes == 2
    assert engine.save_path == "test_q.npy"


@patch("cop_thief.services.training_engine.GameState")
def test_run_headless_games(mock_game_state_class, mock_config, tmp_path):
    q_table = MagicMock(spec=QTable)
    q_table.epsilon = 1.0
    q_table.choose_action.return_value = "up"
    q_table.encode_state.return_value = 0

    mock_game = MagicMock()
    mock_game.cop.row = 2
    mock_game.cop.col = 2
    mock_game.cop.get_position.return_value = (2, 2)
    mock_game.thief.row = 0
    mock_game.thief.col = 0
    mock_game.thief.get_position.return_value = (0, 0)
    mock_game.grid.rows = 5
    mock_game.grid.cols = 5
    mock_game.grid.is_barrier.return_value = False
    mock_game_state_class.return_value = mock_game

    mock_config._config["training"]["save_path"] = str(tmp_path / "test_q.npy")
    mock_config._config["training"]["log_path"] = str(tmp_path / "test_log.jsonl")

    engine = TrainingEngine(mock_config, q_table)
    engine.run_headless_games()

    assert q_table.save.called
    assert q_table.update_bellman.called
    assert len(engine.logs) == 2


def test_save_training_log(mock_config, tmp_path):
    q_table = MagicMock(spec=QTable)
    log_path = tmp_path / "test_log.jsonl"
    mock_config._config["training"]["log_path"] = str(log_path)

    engine = TrainingEngine(mock_config, q_table)
    engine.logs = [{"episode": 0, "moves": 10}]
    engine.save_training_log()

    with open(log_path) as f:
        content = f.read()
    assert "episode" in content
    assert "moves" in content
