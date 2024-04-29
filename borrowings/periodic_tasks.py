import asyncio
import datetime

from datetime import timedelta
from celery import shared_task
from aiogram import Bot

from library_service import settings
from borrowings.models import Borrowing


@shared_task
def send_overdue_borrowing_notification():
    time_now = datetime.datetime.now()
    tomorrow = time_now + timedelta(days=1)

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow,
        actual_return_date__isnull=True
    )

    bot = Bot(token=settings.TELEGRAM_TOKEN)
    chat_id = settings.CHAT_ID

    if not overdue_borrowings:
        asyncio.run(bot.send_message(
            chat_id=chat_id, text="No borrowings overdue today!")
        )

    for borrowing in overdue_borrowings:
        loop = asyncio.get_event_loop()

        message_text = (
            f"overdue_borrowing_id: {borrowing.id}, "
            f"book: {borrowing.book}, "
            f"user: {borrowing.user}, "
            f"expected_return_day: {borrowing.expected_return_date}"
        )

        loop.run_until_complete(bot.send_message(chat_id=chat_id, text=message_text))
        loop.run_until_complete(asyncio.sleep(1))
