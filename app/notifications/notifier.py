"""Optional email notification for important audit events.

Set PROFILEOSINT_SMTP_HOST, PROFILEOSINT_SMTP_PORT, PROFILEOSINT_SMTP_USER,
PROFILEOSINT_SMTP_PASSWORD, PROFILEOSINT_ALERT_FROM, and
PROFILEOSINT_ALERT_TO to enable notifications. Without these variables the
notifier remains disabled and never blocks the application.
"""
import os
import smtplib
import logging
from email.message import EmailMessage
from typing import Any, Dict

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.host = os.getenv("PROFILEOSINT_SMTP_HOST")
        self.port = int(os.getenv("PROFILEOSINT_SMTP_PORT", "587"))
        self.user = os.getenv("PROFILEOSINT_SMTP_USER")
        self.password = os.getenv("PROFILEOSINT_SMTP_PASSWORD")
        self.sender = os.getenv("PROFILEOSINT_ALERT_FROM", self.user or "")
        self.recipient = os.getenv("PROFILEOSINT_ALERT_TO")

    @property
    def enabled(self) -> bool:
        return bool(self.host and self.sender and self.recipient)

    def notify_important(self, operation: str, status: str,
                         details: Dict[str, Any] | None = None,
                         error_message: str | None = None) -> bool:
        if not self.enabled or (status not in {"failure", "denied"} and operation not in {"profile_delete", "audit_export_csv"}):
            return False
        message = EmailMessage()
        message["Subject"] = f"ProfileOSINT alert: {operation} ({status})"
        message["From"] = self.sender
        message["To"] = self.recipient
        message.set_content(f"operation={operation}\nstatus={status}\ndetails={details or {}}\nerror={error_message or ''}")
        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
                smtp.starttls()
                if self.user and self.password:
                    smtp.login(self.user, self.password)
                smtp.send_message(message)
            return True
        except Exception:
            logger.exception("Audit notification failed")
            return False
