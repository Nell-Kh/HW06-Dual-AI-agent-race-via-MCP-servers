import json
import smtplib
from email.mime.text import MIMEText

from cop_thief.shared.config_loader import ConfigLoader
from cop_thief.shared.secrets_manager import SecretsManager


class GmailReporter:
    def __init__(self, config: ConfigLoader, secrets: SecretsManager):
        report_cfg = config.get_config().get("report", {})
        self.recipient = report_cfg.get("recipient", "rmisegal+uoh26b@gmail.com")
        self.sender = secrets.get_gmail_sender()
        self.password = secrets.get_gmail_password()

    def send_report(self, report_dict: dict) -> bool:
        try:
            body = json.dumps(report_dict, indent=2)
            msg = MIMEText(body)
            msg["Subject"] = f"HW06 Results - {report_dict.get('group_name', 'yanel11')}"
            msg["From"] = self.sender
            msg["To"] = self.recipient

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)

            with open("results/email_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Successfully sent report to {self.recipient}\n")
            return True
        except Exception as e:
            import os

            os.makedirs("results", exist_ok=True)
            with open("results/email_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Failed to send report: {e}\n")
            return False
