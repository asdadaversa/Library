import asyncio

from celery import shared_task
from aiogram import Bot

from library_service import settings
from borrowings.models import Borrowing


@shared_task
def send_borrowing_notification(borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
    book = borrowing.book.title
    user = borrowing.user
    message_text = (
        f"New borrowing created, "
        f"id: {borrowing.id}, "
        f"book: {book}, expected return day: {borrowing.expected_return_date} "
        f"user: {user}, full name: {user.first_name} {user.last_name}"
    )
    bot = Bot(token=settings.TELEGRAM_TOKEN)
    chat_id = settings.CHAT_ID
    asyncio.run(bot.send_message(chat_id=chat_id, text=message_text))
    bot.close()
