import asyncio

from celery import shared_task
from aiogram import Bot

from library_service import settings
from payments.models import Payment


@shared_task
def send_success_payment_notification(session_id):
    payment = Payment.objects.get(session=session_id)
    borrowing = payment.borrowing
    user = payment.borrowing.user
    message_text = (
        f"The payment was successful, "
        f"borrowing: {borrowing}, "
        f"user: {user}, "
        f"total: ${payment.money_to_pay}, "
        f"payment id: {payment.session}"
    )
    bot = Bot(token=settings.TELEGRAM_TOKEN)
    chat_id = settings.CHAT_ID
    asyncio.run(bot.send_message(chat_id=chat_id, text=message_text))
    bot.close()
