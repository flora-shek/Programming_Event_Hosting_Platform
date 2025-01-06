# email_utils.py

import yagmail
from django.conf import settings

class YagmailWrapper:
    def __init__(self):
        # Initialize Yagmail with Gmail credentials
        self.yag = yagmail.SMTP(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    def send_email(self, to, subject, body, attachments=None):
        try:
            self.yag.send(to=to, subject=subject, contents=body, attachments=attachments)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

