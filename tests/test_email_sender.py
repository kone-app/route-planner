import pytest
from unittest.mock import patch, MagicMock
import journey_service.notifier as email_sender  


def test_send_email_success():
    body_text = ["Test line 1", "Test line 2"]

    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = email_sender.send_email(body_text)

        # Assertions
        assert result == "Email Sent"
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            email_sender.config.FROM_EMAIL,
            email_sender.config.GMAIL_APP_PASSWORD
        )
        mock_server.send_message.assert_called_once()


def test_send_email_failure():
    body_text = ["Failure test"]

    with patch("smtplib.SMTP", side_effect=Exception("SMTP Error")):
        result = email_sender.send_email(body_text)

        assert result == "Email Failed"

