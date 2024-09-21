from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from mood_mate_src.filters import AdminFilter
from mood_mate_src.database_tools.users import get_all_users_from_db, User
from mood_mate_src.states_machine import SettingsStates
from mood_mate_src.messaging.send import send_message_to_user
from mood_mate_src.messaging.states_text import get_state_msg
from mood_mate_src.database_tools.users import (
    process_user_db,
    update_user_in_db,
    process_user_from_id,
    Language,
)
from mood_mate_src.filters import ButtonTextFilter, CallbackDataFilter, validate_number_input
from mood_mate_src.keyboard import (
    get_all_buttons_text,
    get_inline_settings_keyboard,
    get_settings_keyboard,
    get_start_keyboard,
)


from mood_mate_src.filters import AdminFilter
from mood_mate_src.database_tools.users import get_all_users_from_db, User
from mood_mate_src.analytics.user_analytics import get_user_statistics_text

from mood_mate_src.messaging.send import send_message_to_user

from mood_mate_src.messaging.notifications import weekly_report

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
        await message.answer("Please provide text to send.")
    for user in users:
        await send_message_to_user(user.chat_id, text)
        
@router.message(ButtonTextFilter(get_all_buttons_text("settings")))
async def settings_handler(message: Message):
    user = await process_user_db(message)
    await message.answer("Settings", reply_markup=get_inline_settings_keyboard(user=user))

# Add settings callbacks:

@router.callback_query(CallbackDataFilter("change_language"))
async def change_language_callback_handler(query: types.CallbackQuery):
    user = await process_user_from_id(query.from_user.id)
    new_lang = Language.RU.value if user.settings.language == Language.ENG.value else Language.ENG.value
    user.settings.language = new_lang
    await update_user_in_db(user)
    await query.answer()
    await query.message.edit_text(f"{get_state_msg('lang_changed', user)}",
                                  reply_markup=get_inline_settings_keyboard(user=user))


@router.callback_query(CallbackDataFilter("toggle_reminder"))
async def toggle_reminder_callback_handler(query: types.CallbackQuery):
    user = await process_user_from_id(query.from_user.id)
    user.settings.reminder_enabled = not user.settings.reminder_enabled
    await update_user_in_db(user)
    await query.answer()
    reminder_state = "on" if user.settings.reminder_enabled else "off"
    await query.message.edit_text(f"{get_state_msg('toggle_reminder_' + reminder_state, user)}",
                                  reply_markup=get_inline_settings_keyboard(user=user))

@router.message(ButtonTextFilter(get_all_buttons_text("toggle_reminder")))
async def toggle_reminder_handler(message: Message):
    user = await process_user_db(message)
    user.settings.reminder_enabled = not user.settings.reminder_enabled
    await update_user_in_db(user)
    reminder_state = "on" if user.settings.reminder_enabled else "off"
    await message.answer(f"{get_state_msg('toggle_reminder_' + reminder_state, user)}",
                         reply_markup=get_settings_keyboard(user=user))

@router.message(ButtonTextFilter(get_all_buttons_text("change_language")))
async def change_language_handler(message: Message):
    user = await process_user_db(message)
    new_lang = Language.RU.value if user.settings.language == Language.ENG.value else Language.ENG.value
    user.settings.language = new_lang
    await update_user_in_db(user)
    await message.answer(f"{get_state_msg('lang_changed', user)}", reply_markup=get_settings_keyboard(user=user))
    
@router.callback_query(CallbackDataFilter("set_recommended_sleep"))
async def set_recommended_sleep_callback_handler(query: types.CallbackQuery, state: FSMContext):
    '''Send user to the recommended_sleep state of FSM'''
    user = await process_user_from_id(query.from_user.id)
    await state.set_state(SettingsStates.recommended_sleep)
    await query.answer()
    await query.message.edit_text(get_state_msg("recommended_sleep", user))
    
@router.message(SettingsStates.recommended_sleep)
async def set_recommended_sleep_handler(message: Message, state: FSMContext):
    '''Set the recommended_sleep value to the user'''
    user = await process_user_db(message)
    number = validate_number_input(message.text)
    if number is False:
        await message.answer(get_state_msg("invalid_number_input", user))
        await state.set_state(SettingsStates.recommended_sleep)
    user.settings.recommended_sleep = float(message.text)
    await update_user_in_db(user)
    await state.clear()
    await message.answer(get_state_msg("recommended_sleep_set", user), reply_markup=get_start_keyboard(user=user))   
@router.message(Command("get_stats"), AdminFilter())
async def get_stats(message: types.Message) -> None:
    stats = get_user_statistics_text()
    await message.answer(stats)
    
@router.message(Command("send_weekly_report"), AdminFilter())
async def send_weekly_report(message: types.Message) -> None:
    await weekly_report()
    await message.answer("Weekly report sent.")
