from unittest.mock import MagicMock, patch

from cop_thief.services.gmail_reporter import GmailReporter
from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.secrets_manager import SecretsManager


def get_mock_config():
    config = ConfigLoader()
    config._config = {"report": {"recipient": "test@test.com"}}
    return config


def get_mock_secrets():
    secrets = SecretsManager()
    secrets.get_gmail_sender = MagicMock(return_value="sender@test.com")
    secrets.get_gmail_password = MagicMock(return_value="pass")
    return secrets


@patch("smtplib.SMTP")
def test_send_report_success(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    reporter = GmailReporter(get_mock_config(), get_mock_secrets())
    report = {"group_name": "test_group"}
    res = reporter.send_report(report)
    assert res is True
    mock_server.send_message.assert_called_once()


@patch("smtplib.SMTP")
def test_send_report_failure_returns_false(mock_smtp):
    mock_smtp.side_effect = Exception("Failed")

    reporter = GmailReporter(get_mock_config(), get_mock_secrets())
    res = reporter.send_report({})
    assert res is False


@patch("smtplib.SMTP")
def test_email_subject_correct(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    reporter = GmailReporter(get_mock_config(), get_mock_secrets())
    report = {"group_name": "my_group"}
    reporter.send_report(report)

    # Check the msg subject
    msg = mock_server.send_message.call_args[0][0]
    assert msg["Subject"] == "HW06 Results - my_group"
