"""
Notification dispatch service.
Handles in-app, email (SendGrid), and WhatsApp (Twilio) channels.
"""
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType, NotificationChannel
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    async def send(
        self,
        db: AsyncSession,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.info,
        channel: NotificationChannel = NotificationChannel.in_app,
        shipment_id: int = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            shipment_id=shipment_id,
            type=notification_type,
            channel=channel,
            title=title,
            message=message,
        )
        db.add(notification)
        await db.flush()

        if channel == NotificationChannel.whatsapp:
            await self._send_whatsapp(message)
        elif channel == NotificationChannel.email:
            await self._send_email(title, message)

        return notification

    async def _send_whatsapp(self, message: str) -> bool:
        """Send WhatsApp message via Twilio."""
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.debug("Twilio credentials not configured — skipping WhatsApp")
            return False
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    url,
                    data={"From": settings.TWILIO_WHATSAPP_FROM, "Body": message},
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                )
                return resp.status_code == 201
        except Exception as e:
            logger.warning(f"WhatsApp send failed: {e}")
            return False

    async def _send_email(self, subject: str, body: str) -> bool:
        """Send email via SendGrid."""
        if not settings.SENDGRID_API_KEY:
            logger.debug("SendGrid key not configured — skipping email")
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"},
                    json={
                        "personalizations": [{"to": [{"email": settings.EMAIL_FROM}]}],
                        "from": {"email": settings.EMAIL_FROM},
                        "subject": subject,
                        "content": [{"type": "text/plain", "value": body}],
                    },
                )
                return resp.status_code == 202
        except Exception as e:
            logger.warning(f"Email send failed: {e}")
            return False


notification_service = NotificationService()
