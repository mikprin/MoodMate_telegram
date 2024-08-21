from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from os import getenv

from mood_mate_src.filters import AdminFilter
from mood_mate_src.database_tools.users import get_all_users_from_db, User

from mood_mate_src.messaging.send import send_message_to_user




router = Router()

@router.edited_message()
async def edited_message_handler(edited_message: types.Message) -> None:
    await edited_message.answer("Please note: Edited message are not supported yet.")
    
    
@router.message(Command("send_message_to_users"), AdminFilter())
async def send_message_to_users(message: types.Message) -> None:
    users = get_all_users_from_db()
    text = message.text
    # Remove /send_message_to_users from the text
    text = text.replace("/send_message_to_users", "")
    if len(text) == 0 or text.isspace():
        await message.answer("Please provide the text to send.")
    for user in users:
        await send_message_to_user(user.chat_id, text)