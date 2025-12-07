from __future__ import annotations

import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail

logger = logging.getLogger(__name__)


class MailError(Exception):
    """Raised when mail sending fails."""


class Mailer:
    def __init__(self, api_key: str, from_email: str, from_name: str, to_email: str):
        self._client = SendGridAPIClient(api_key)
        self._from_email = Email(email=from_email, name=from_name)
        self._to_email = to_email

    def send(self, subject: str, text_body: str, html_body: str | None = None) -> None:
        mail = Mail(
            from_email=self._from_email,
            to_emails=self._to_email,
            subject=subject,
            plain_text_content=text_body,
            html_content=html_body,
        )
        try:
            response = self._client.send(mail)
            logger.info("Mail sent with status %s", response.status_code)
        except Exception as exc:  # noqa: BLE001
            raise MailError(f"Failed to send email: {exc}") from exc
