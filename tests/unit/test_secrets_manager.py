import os
from unittest.mock import patch

import pytest

from cop_thief.shared.secrets_manager import SecretsManager


def test_get_openai_key_missing():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError) as exc_info:
            SecretsManager.get_openai_key()
        assert "OPENAI_API_KEY is missing" in str(exc_info.value)


def test_get_gmail_sender_missing():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError) as exc_info:
            SecretsManager.get_gmail_sender()
        assert "GMAIL_SENDER is missing" in str(exc_info.value)


def test_get_gmail_password_missing():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError) as exc_info:
            SecretsManager.get_gmail_password()
        assert "GMAIL_APP_PASSWORD is missing" in str(exc_info.value)


@patch("cop_thief.shared.secrets_manager.load_dotenv")
def test_load_env_success(mock_load_dotenv):
    SecretsManager()
    mock_load_dotenv.assert_called_once()

    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test_key",
            "GMAIL_SENDER": "test@gmail.com",
            "GMAIL_APP_PASSWORD": "test_password",
        },
        clear=True,
    ):
        assert SecretsManager.get_openai_key() == "test_key"
        assert SecretsManager.get_gmail_sender() == "test@gmail.com"
        assert SecretsManager.get_gmail_password() == "test_password"
