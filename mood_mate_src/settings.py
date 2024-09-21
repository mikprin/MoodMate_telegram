from aiogram import Router, F
from aiogram import types
from aiogram.types import InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from mood_mate_src.filters import ButtonTextFilter, CallbackDataFilter
from mood_mate_src.database_tools.users import (
    User,
    UserSettings,
    Language,
    process_user_db,
    process_user_from_id,
    update_user_in_db
)
from mood_mate_src.keyboard import (
    get_all_buttons_text,
    BUTTONS_TEXT_LANG,
    get_inline_keyboard_buttons_from_list,
    get_settings_keyboard,
    get_inline_settings_keyboard
)
from mood_mate_src.mate_logger import logger
from mood_mate_src.messaging.states_text import get_state_msg


router = Router()


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
    
def create_toggle_handler(setting_name: str):
    """
    Creates a handler to toggle a specific boolean setting for the user.
    """
    async def toggle_handler(query: types.CallbackQuery):
        user = await process_user_from_id(query.from_user.id)
        current_value = getattr(user.settings, setting_name)
        if current_value is not None:
            setattr(user.settings, setting_name, not current_value)  # Toggle the setting
        else:
            setattr(user.settings, setting_name, True)
        await update_user_in_db(user)
        await query.answer()
        
        # Generate the message based on the new state
        new_state = "on" if getattr(user.settings, setting_name) else "off"
        message_key = f"toggle_{setting_name}_{new_state}"
        await query.message.edit_text(
            get_state_msg(message_key, user),
            reply_markup=get_inline_settings_keyboard(user=user)
        )
    
    return toggle_handler


router.callback_query(CallbackDataFilter("toggle_weekly_report"))(create_toggle_handler("weekly_report_enabled"))