import json

import pytest

from src.cop_thief.shared.config_loader import ConfigLoader


@pytest.fixture
def valid_config_file(tmp_path):
    config_data = {
        "version": "1.00",
        "grid_size": [5, 5],
        "max_moves": 25,
        "num_games": 6,
        "max_barriers": 5,
        "scoring": {
            "cop_win": 20,
            "thief_win": 10,
            "cop_loss": 5,
            "thief_loss": 5
        },
        "agents": {
            "cop_start": "random",
            "thief_start": "random"
        },
        "llm": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-6",
            "max_tokens": 1000,
            "temperature": 0.7
        },
        "mcp": {
            "cop_server_port": 8001,
            "thief_server_port": 8002,
            "host": "127.0.0.1"
        },
        "rl": {
            "learning_rate": 0.1,
            "discount_factor": 0.9,
            "epsilon": 0.2
        },
        "report": {
            "recipient": "rmisegal+uoh26b@gmail.com",
            "timezone": "Asia/Jerusalem",
            "group_name": "YOUR_GROUP_NAME",
            "github_repo": "https://github.com/Nell-Kh/HW06-Dual-AI-agent-race-via-MCP-servers"
        }
    }
    file_path = tmp_path / "config.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    return str(file_path)


def test_load_success(valid_config_file):
    loader = ConfigLoader(config_path=valid_config_file)
    loader.load()
    assert loader._config is not None


def test_load_missing_file():
    loader = ConfigLoader(config_path="non_existent_file.json")
    with pytest.raises(FileNotFoundError):
        loader.load()


def test_load_invalid_json(tmp_path):
    file_path = tmp_path / "invalid_config.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{invalid_json: 123")

    loader = ConfigLoader(config_path=str(file_path))
    with pytest.raises(ValueError):
        loader.load()


def test_get_grid_size(valid_config_file):
    loader = ConfigLoader(config_path=valid_config_file)
    loader.load()
    size = loader.get_grid_size()
    assert size == [5, 5]


def test_get_scoring_keys(valid_config_file):
    loader = ConfigLoader(config_path=valid_config_file)
    loader.load()
    scoring = loader.get_scoring()
    assert "cop_win" in scoring
    assert "thief_win" in scoring
    assert "cop_loss" in scoring
    assert "thief_loss" in scoring
    assert scoring["cop_win"] == 20


def test_get_mcp_ports(valid_config_file):
    loader = ConfigLoader(config_path=valid_config_file)
    loader.load()
    ports = loader.get_mcp_ports()
    assert ports["cop_server_port"] == 8001
    assert ports["thief_server_port"] == 8002


def test_validate_missing_key(tmp_path):
    config_data = {"version": "1.00"}
    file_path = tmp_path / "incomplete_config.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f)

    loader = ConfigLoader(config_path=str(file_path))
    with pytest.raises(KeyError) as exc_info:
        loader.load()
    assert "Missing required config key" in str(exc_info.value)


def test_num_states_dynamic(valid_config_file):
    loader = ConfigLoader(config_path=valid_config_file)
    loader.load()
    assert loader.get_num_states() == 25
