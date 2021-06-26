from unittest.mock import patch
from email.message import EmailMessage

from otter_buddy.constants import MAIL_USER
from otter_buddy.utils.email.emailconn import EmailConn


def test_send_email():
    email = "test@test.com"
    content = "This is a test message for email\nGreats!"
    subject = "Test Subject"

    expected_message = EmailMessage()
    expected_message.set_content(content)
    expected_message["Subject"] = subject
    expected_message["From"] = MAIL_USER
    expected_message["To"] = email

    with patch('smtplib.SMTP_SSL', autospec=True) as mock_smtp:
        conn = EmailConn()
        conn.send_mail(email, subject, content)

        mock_smtp.assert_called()

        context = mock_smtp.return_value.__enter__.return_value
        context.ehlo.assert_called()
        context.login.assert_called()
        context.sendmail.assert_called_with(MAIL_USER, email, expected_message.as_string())
