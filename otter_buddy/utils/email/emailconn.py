import os
import ssl
import smtplib
import logging

from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailConn(object):
    _instance = None

    def __new__(self):
        if self._instance is None:
            load_dotenv()
            self.mail_user = os.environ.get("MAIL_USER")
            self.mail_pass = os.environ.get("MAIL_PASS")
            self._instance = super(EmailConn, self).__new__(self)
        
        return self._instance
    
    def send_mail(self, to: str, subject: str, content: str):
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = self.mail_user
        message["To"] = to
        message.attach(MIMEText(content, "plain"))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.mail_user, self.mail_pass)
                server.sendmail(
                    self.mail_user, to, message.as_string()
                )
        except Exception as e:
            logger.error("Error while sending the email")
            logger.error(e)
