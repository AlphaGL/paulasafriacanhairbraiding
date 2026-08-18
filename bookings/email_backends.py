"""
Sends email through Resend's HTTP API instead of raw SMTP. Plugs into Django's
normal EmailBackend interface, so nothing elsewhere (bookings/emails.py) needs
to change — only settings.EMAIL_BACKEND points here when RESEND_API_KEY is set.

Chosen over SMTP for the Vercel deployment: SMTP needs a synchronous, blocking
socket connection from inside a serverless function, which can occasionally
stall past Vercel's function timeout. An HTTP POST is a single fast round trip.
"""

import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        resend.api_key = settings.RESEND_API_KEY
        sent_count = 0

        for message in email_messages:
            payload = {
                "from": message.from_email,
                "to": list(message.to),
                "subject": message.subject,
                "text": message.body,
            }
            if message.reply_to:
                payload["reply_to"] = list(message.reply_to)

            try:
                resend.Emails.send(payload)
                sent_count += 1
            except Exception:
                if not self.fail_silently:
                    raise

        return sent_count
