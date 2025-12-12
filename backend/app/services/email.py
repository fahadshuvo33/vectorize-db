"""
Email service for sending verification and notification emails.
Since Supabase handles email verification automatically, this service
is mainly for custom emails and notifications.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email"""
        if not self.smtp_host:
            logger.warning("SMTP not configured, skipping email send")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)

            part2 = MIMEText(html_content, "html")
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_welcome_email(self, to_email: str, full_name: Optional[str] = None):
        """Send welcome email after successful registration"""
        name = full_name or "there"
        subject = "Welcome to VectorizeDB!"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">Welcome to VectorizeDB, {name}! 🎉</h2>
                    <p>Thank you for joining VectorizeDB! You're now ready to turn your databases into AI-ready formats with our powerful chatbot.</p>
                    
                    <h3>What you can do:</h3>
                    <ul>
                        <li>Upload Excel, CSV, SQL dumps, or JSON files</li>
                        <li>Get instant vector embeddings and JSONL exports</li>
                        <li>Chat with your data using our live AI chatbot</li>
                        <li>Download RAG-ready code for your projects</li>
                    </ul>
                    
                    <p style="margin-top: 30px;">
                        <a href="{settings.FRONTEND_URL}/dashboard" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            Go to Dashboard
                        </a>
                    </p>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Need help? Reply to this email or visit our <a href="{settings.FRONTEND_URL}/docs">documentation</a>.
                    </p>
                </div>
            </body>
        </html>
        """

        text_content = f"""
        Welcome to VectorizeDB, {name}!
        
        Thank you for joining VectorizeDB! You're now ready to turn your databases into AI-ready formats.
        
        What you can do:
        - Upload Excel, CSV, SQL dumps, or JSON files
        - Get instant vector embeddings and JSONL exports
        - Chat with your data using our live AI chatbot
        - Download RAG-ready code for your projects
        
        Go to Dashboard: {settings.FRONTEND_URL}/dashboard
        
        Need help? Reply to this email or visit our documentation.
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_password_set_confirmation(
        self, to_email: str, full_name: Optional[str] = None
    ):
        """Send confirmation email after password is set on social account"""
        name = full_name or "there"
        subject = "Password Added to Your Account"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">Password Added Successfully</h2>
                    <p>Hi {name},</p>
                    <p>A password has been successfully added to your VectorizeDB account. You can now sign in using either:</p>
                    
                    <ul>
                        <li>Your social login (Google/GitHub)</li>
                        <li>Email and password</li>
                    </ul>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #FEF3C7; border-left: 4px solid #F59E0B;">
                        <strong>Security Notice:</strong> If you didn't add this password, please contact support immediately.
                    </p>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Questions? Contact us at support@vectorizedb.com
                    </p>
                </div>
            </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)


from functools import lru_cache


@lru_cache()
def get_email_service() -> EmailService:
    """Get email service instance (cached)"""
    return EmailService()


# Export for backward compatibility
email_service = get_email_service()
