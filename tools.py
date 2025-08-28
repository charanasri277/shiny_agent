import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import requests
from livekit.agents import function_tool, RunContext

# --- WEATHER TOOL (simple: wttr.in) ---
@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """
    Get a quick weather line for a city using wttr.in.
    """
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
        if r.status_code == 200:
            logging.info("Weather for %s: %s", city, r.text.strip())
            return r.text.strip()
        return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.exception("Weather error: %s", e)
        return f"An error occurred while retrieving weather for {city}."

# --- GMAIL TOOL (SMTP with app password) ---
@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None,
) -> str:
    """
    Send an email via Gmail SMTP (requires GMAIL_USER and GMAIL_APP_PASSWORD in environment).
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        return "Email sending failed: Gmail credentials not configured."

    try:
        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject
        recipients = [to_email]
        if cc_email:
            msg["Cc"] = cc_email
            recipients.append(cc_email)

        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipients, msg.as_string())
        server.quit()
        return f"Email sent to {to_email}."
    except smtplib.SMTPAuthenticationError:
        return "Email sending failed: authentication error."
    except Exception as e:
        return f"Email sending failed: {e}"
