import json
from unittest.mock import MagicMock, patch

import pytest

from cop_thief.shared.api_gatekeeper import ApiGatekeeper
from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.llm_client import LLMClient
from cop_thief.shared.secrets_manager import SecretsManager


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
            "provider": "openai",
            "model": "gpt-4o-mini",
            "max_tokens": 1000,
            "temperature": 0.7,
        },
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


@pytest.fixture
def mock_secrets():
    sm = MagicMock(spec=SecretsManager)
    sm.get_openai_key.return_value = "test-key"
    return sm


def create_mock_response(content):
    mock_msg = MagicMock()
    mock_msg.message.content = content
    mock_resp = MagicMock()
    mock_resp.choices = [mock_msg]
    return mock_resp


def test_generate_move_valid_direction(mock_config, mock_secrets):
    client = LLMClient(mock_config, mock_secrets)
    with patch.object(client.client.chat.completions, "create") as mock_create:
        mock_create.return_value = create_mock_response("up")
        result = client.generate_move("cop", "obs", ["up", "down"], [])
        assert result["action"] == "up"


def test_generate_move_invalid_response(mock_config, mock_secrets):
    client = LLMClient(mock_config, mock_secrets)
    with patch.object(client.client.chat.completions, "create") as mock_create:
        mock_create.return_value = create_mock_response("banana")
        result = client.generate_move("cop", "obs", ["left", "right"], [])
        assert result["action"] == "left"


def test_generate_move_case_insensitive(mock_config, mock_secrets):
    client = LLMClient(mock_config, mock_secrets)
    with patch.object(client.client.chat.completions, "create") as mock_create:
        mock_create.return_value = create_mock_response("UP")
        result = client.generate_move("cop", "obs", ["up", "down"], [])
        assert result["action"] == "up"


def test_parse_direction_finds_direction_in_sentence(mock_config, mock_secrets):
    client = LLMClient(mock_config, mock_secrets)
    result = client.prompt_builder.parse_direction("I should go up now", ["up", "down"])
    assert result == "up"


def test_barrier_decision_returns_valid_action(mock_config, mock_secrets):
    client = LLMClient(mock_config, mock_secrets)
    with patch.object(client.client.chat.completions, "create") as mock_create:
        mock_create.return_value = create_mock_response("place_barrier")
        result = client.generate_barrier_decision("obs", ["up", "down"], 5)
        assert result["action"] == "place_barrier"


def test_gatekeeper_retries_on_failure(mock_config):
    gatekeeper = ApiGatekeeper(mock_config)
    mock_api = MagicMock(side_effect=Exception("API Error"))
    with patch("time.sleep"):
        with pytest.raises(Exception, match="API Error"):
            gatekeeper.execute(mock_api)
        assert mock_api.call_count == 4


def test_gatekeeper_logs_calls(mock_config, tmp_path):
    gatekeeper = ApiGatekeeper(mock_config)
    log_file = tmp_path / "api_calls.log"
    import logging

    gatekeeper.logger.handlers.clear()
    fh = logging.FileHandler(str(log_file))
    gatekeeper.logger.addHandler(fh)

    mock_api = MagicMock(return_value="success")
    mock_api.__name__ = "mock_api"
    gatekeeper.execute(mock_api)

    with open(log_file) as f:
        log_content = f.read()
    assert "mock_api - SUCCESS" in log_content
