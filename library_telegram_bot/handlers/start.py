from aiogram import Router, Bot, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from library_service import settings

bot = Bot(token=settings.TELEGRAM_TOKEN)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    return message.answer(f"Lets start...your chat id is: {message.chat.id}")
