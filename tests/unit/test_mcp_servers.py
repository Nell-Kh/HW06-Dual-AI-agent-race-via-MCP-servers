import json

import pytest

from cop_thief.services.cop_mcp_server import CopMCPServer
from cop_thief.services.thief_mcp_server import ThiefMCPServer
from cop_thief.shared.config_loader import ConfigLoader


@pytest.fixture
def mock_config(tmp_path):
    data = {
        "version": "1.0",
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

def test_cop_server_observe_returns_string(mock_config):
    server = CopMCPServer(mock_config)
    res = server._observe()
    assert isinstance(res, str)
    assert len(res) > 0

def test_cop_server_valid_moves_returns_list(mock_config):
    server = CopMCPServer(mock_config)
    res = server._get_valid_moves()
    assert isinstance(res, list)

def test_thief_server_observe_returns_string(mock_config):
    server = ThiefMCPServer(mock_config)
    res = server._observe()
    assert isinstance(res, str)
    assert len(res) > 0

def test_thief_server_no_barrier_tool(mock_config):
    server = ThiefMCPServer(mock_config)
    # Using python's hasattr or check our explicit test exposures
    assert not hasattr(server, "place_barrier")
