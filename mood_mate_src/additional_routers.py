from aiogram import Router, F
from aiogram import types

router = Router()

@router.edited_message()
async def edited_message_handler(edited_message: types.Message) -> None:
    await edited_message.answer("Please note: Edited message are not supported yet.")