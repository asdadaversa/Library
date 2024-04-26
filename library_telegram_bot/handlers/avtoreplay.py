from aiogram import Router, types

router = Router()


@router.message()
async def answer(message: types.Message):
    await message.answer("It is library telegram bot, contact the administrator brat_bake@gmail.com")
