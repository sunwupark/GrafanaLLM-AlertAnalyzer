"""
Email Notification Service
"""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.conf.config import settings
from app.conf.logging import logger
from app.utils.text import clean_text, format_html_text


def send_email_alert(alert_description, analysis_result):
    if not all([settings.SMTP_SERVER, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
        logger.warning("SMTP settings not configured. Email notification skipped.")
        return

    recipients = settings.ALERT_RECIPIENTS.split(",")
    if not recipients or not recipients[0]:
        logger.warning("No recipients configured. Email notification skipped.")
        return

    clean_description = clean_text(alert_description)
    if len(clean_description) > 50:
        subject = f"Alert Analysis: {clean_description[:50]}..."
    else:
        subject = f"Alert Analysis: {clean_description}"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <h2 style="color: #d9534f;">Alert Analysis Report</h2>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <p><strong>Alert Description:</strong> {clean_text(alert_description)}</p>
            <p><strong>Analysis Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div style="border-left: 4px solid #d9534f; padding-left: 15px; margin-bottom: 20px;">
            <h3 style="color: #d9534f;">Problem:</h3>
            <p>{clean_text(analysis_result["problem"])}</p>
        </div>
        
        <div style="border-left: 4px solid #f0ad4e; padding-left: 15px; margin-bottom: 20px;">
            <h3 style="color: #f0ad4e;">Cause of Problem:</h3>
            <p>{clean_text(analysis_result["cause"])}</p>
        </div>
        
        <div style="border-left: 4px solid #5cb85c; padding-left: 15px;">
            <h3 style="color: #5cb85c;">Solution:</h3>
            {format_html_text(analysis_result["solution"])}
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_USERNAME
    message["To"] = ", ".join(recipients)

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USERNAME, recipients, message.as_string())
        logger.info(f"Email alert sent to {', '.join(recipients)}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
