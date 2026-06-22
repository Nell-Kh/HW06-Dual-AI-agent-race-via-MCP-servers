import os

from dotenv import load_dotenv


class SecretsManager:
    """Manages sensitive credentials and API keys via environment variables."""

    @staticmethod
    def load_env() -> None:
        """Loads .env file via python-dotenv into os.environ."""
        load_dotenv()

    @staticmethod
    def get_openai_key() -> str:
        """Returns OPENAI_API_KEY, raises KeyError if missing."""
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise KeyError("OPENAI_API_KEY is missing from environment variables")
        return key

    @staticmethod
    def get_gmail_sender() -> str:
        """Returns GMAIL_SENDER, raises KeyError if missing."""
        sender = os.environ.get("GMAIL_SENDER")
        if not sender:
            raise KeyError("GMAIL_SENDER is missing from environment variables")
        return sender

    @staticmethod
    def get_gmail_password() -> str:
        """Returns GMAIL_APP_PASSWORD, raises KeyError if missing."""
        password = os.environ.get("GMAIL_APP_PASSWORD")
        if not password:
            raise KeyError("GMAIL_APP_PASSWORD is missing from environment variables")
        return password
