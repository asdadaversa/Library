import asyncio

from aiogram import Bot, Dispatcher

from handlers import start, avtoreplay
from library_service import settings


async def main():
    bot = Bot(token=settings.TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(avtoreplay.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
