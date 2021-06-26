import os
import ssl
import smtplib
import logging

from dotenv import load_dotenv
from email.message import EmailMessage

from otter_buddy.constants import MAIL_USER

logger = logging.getLogger(__name__)


class EmailConn(object):
    _instance = None

    def __new__(self):
        if self._instance is None:
            load_dotenv()
            self.mail_user = MAIL_USER
            self.mail_pass = os.environ.get("MAIL_PASS")
            self._instance = super(EmailConn, self).__new__(self)
        
        return self._instance
    
    def send_mail(self, to: str, subject: str, content: str):
        if not self.mail_user or not self.mail_pass:
            logger.warn("Email not configured")
            return
        message = EmailMessage()
        message.set_content(content)
        message["Subject"] = subject
        message["From"] = self.mail_user
        message["To"] = to

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.ehlo()
                server.login(self.mail_user, self.mail_pass)
                server.sendmail(
                    self.mail_user, to, message.as_string()
                )
        except smtplib.SMTPServerDisconnected :
            logger.error("smtplib.SMTPServerDisconnected")
        except smtplib.SMTPSenderRefused:
            logger.error("smtplib.SMTPSenderRefused")
        except smtplib.SMTPRecipientsRefused:
            logger.error("smtplib.SMTPRecipientsRefused")
        except smtplib.SMTPDataError:
            logger.error("smtplib.SMTPDataError")
        except smtplib.SMTPConnectError:
            logger.error("smtplib.SMTPConnectError")
        except smtplib.SMTPHeloError:
            logger.error("smtplib.SMTPHeloError")
        except smtplib.SMTPAuthenticationError:
            logger.error("smtplib.SMTPAuthenticationError")
        except smtplib.SMTPResponseException as e:
            logger.error("smtplib.SMTPResponseException: " + str(e.smtp_code) + " " + str(e.smtp_error))
        except Exception as e:
            logger.error("Error while sending the email")
            logger.error(e)
