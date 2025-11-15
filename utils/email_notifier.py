"""Email notification utilities."""

import os
import smtplib
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from utils.logger import get_logger

logger = get_logger("email_notifier")


def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> None:
    """Send email notification using SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML version of the email body

    Note:
        Loads SMTP configuration from .env file or environment variables:
        - SMTP_SERVER (e.g., smtp.gmail.com)
        - SMTP_PORT (e.g., 587)
        - SMTP_USERNAME
        - SMTP_PASSWORD
    """
    # Load environment variables from .env file if it exists
    load_dotenv()

    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT", "587")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([smtp_server, smtp_username, smtp_password]):
        logger.warning(
            "SMTP credentials not configured. "
            "Set SMTP_SERVER, SMTP_USERNAME, and SMTP_PASSWORD "
            "environment variables."
        )
        logger.info(f"Email would have been sent to {to_email}")
        logger.info(f"Subject: {subject}")
        logger.debug(f"Body:\n{body}")
        print(
            "Warning: SMTP credentials not configured. "
            "Email not sent."
        )
        return

    try:
        logger.debug(f"Preparing email to {to_email}")
        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_username
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach plain text version
        msg.attach(MIMEText(body, "plain"))

        # Attach HTML version if provided
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
            logger.debug("HTML email body attached")

        logger.debug(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
        with smtplib.SMTP(smtp_server, int(smtp_port), timeout=30) as server:
            server.starttls()
            logger.debug("Logging in to SMTP server")
            server.login(smtp_username, smtp_password)
            logger.debug("Sending message")
            server.send_message(msg)
        logger.info(f"Email notification sent to {to_email}")
        print(f"Email notification sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed")
        print("Warning: Failed to send email: Authentication failed")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        print(f"Warning: Failed to send email: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        print(f"Warning: Failed to send email: {e}")
