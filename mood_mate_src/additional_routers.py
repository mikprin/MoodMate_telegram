# settings and other routers
from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from mood_mate_src.filters import AdminFilter
from mood_mate_src.database_tools.users import get_all_users_from_db, User
from mood_mate_src.states_machine import SettingsStates
from mood_mate_src.messaging.send import send_message_to_chat_id
from mood_mate_src.messaging.states_text import get_state_msg
from mood_mate_src.database_tools.users import (
    process_user_db,
    update_user_in_db,
    process_user_from_id,
)
from mood_mate_src.database_tools.schema import DEFAULT_ASSISTANT_ROLE, Language
from mood_mate_src.filters import ButtonTextFilter, CallbackDataFilter, validate_number_input
from mood_mate_src.keyboard import (
    get_all_buttons_text,
    get_inline_settings_keyboard,
    get_settings_keyboard,
    get_start_keyboard,
    get_button_text,
)


from mood_mate_src.filters import AdminFilter
from mood_mate_src.database_tools.users import get_all_users_from_db, User
from mood_mate_src.analytics.user_analytics import get_user_statistics_text

from mood_mate_src.messaging.send import send_message_to_chat_id
from mood_mate_src.messaging.notifications import weekly_report
from mood_mate_src.analytics.assistants import PREDEFINED_ASSITANT_ROLES, create_short_assistant_name
from mood_mate_src.mate_logger import logger
from mood_mate_src.database_tools.schema import AssistantRole

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
        await send_message_to_chat_id(user.chat_id, text)
        
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


@router.callback_query(CallbackDataFilter("set_assistant_role"))
async def set_assistant_role_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Send user to select a predefined role, enter a custom role, or keep the current role."""
    user = await process_user_from_id(query.from_user.id)
    keyboard = list()

    # Add buttons for each predefined role
    for role in PREDEFINED_ASSITANT_ROLES:
        keyboard.append([types.InlineKeyboardButton(text=role.role_name, callback_data=f"select_role_{role.role_name_short}")])

    # Add a button for custom role input
    keyboard.append([types.InlineKeyboardButton(text=get_button_text("enter_custom_role", user=user),
                                                callback_data="enter_custom_role")])

    # Add a button to keep the current role
    keyboard.append([types.InlineKeyboardButton(text=get_button_text("keep_current_role", user=user),
                                                callback_data="keep_current_role")])

    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    current_role = user.settings.assistant_custom_role
    text = get_state_msg("choose_assistant_role", user)
    if current_role is not None:
        text = text.format(current_role.role_name)
    await state.set_state(SettingsStates.assistant_role)
    await query.answer()
    await query.message.edit_text(text, reply_markup=inline_keyboard)

@router.callback_query(CallbackDataFilter("keep_current_role"))
async def keep_current_role_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Handle keeping the current assistant role."""
    user = await process_user_from_id(query.from_user.id)
    await state.clear()
    await query.answer()
    
    if user.settings.assistant_custom_role is None:
        role_name = DEFAULT_ASSISTANT_ROLE.role_name
    else:
        role_name = user.settings.assistant_custom_role.role_name    
    await query.message.edit_text(get_state_msg("role_unchanged", user).format(role_name))

@router.callback_query(CallbackDataFilter("select_role_"))
async def select_predefined_role_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Handle selection of predefined assistant role."""
    user = await process_user_from_id(query.from_user.id)
    selected_role_short = query.data.replace("select_role_", "")
    selected_role = next((role for role in PREDEFINED_ASSITANT_ROLES if role.role_name_short == selected_role_short), None)
    if selected_role:
        user.settings.assistant_custom_role = selected_role
        await update_user_in_db(user)
        await state.clear()
        await query.answer()
        await query.message.edit_text(get_state_msg("role_set", user).format(selected_role.role_name))

@router.callback_query(CallbackDataFilter("enter_custom_role"))
async def enter_custom_role_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Prompt user to enter a custom role."""
    user = await process_user_from_id(query.from_user.id)
    await state.set_state(SettingsStates.enter_custom_role)
    await query.answer()
    await query.message.edit_text(get_state_msg("enter_custom_role_prompt", user))

@router.message(SettingsStates.enter_custom_role)
async def enter_custom_role_handler(message: Message, state: FSMContext):
    """Handle custom role input from the user."""
    user = await process_user_db(message)
    custom_role_name = message.text.strip()

    if not custom_role_name:
        await message.answer(get_state_msg("invalid_custom_role", user))
        return

    custom_role = AssistantRole(role_name_short=create_short_assistant_name(custom_role_name), role_name=custom_role_name)
    user.settings.assistant_custom_role = custom_role

    await update_user_in_db(user)
    await state.clear()
    await message.answer(get_state_msg("role_set", user).format(custom_role.role_name), reply_markup=get_start_keyboard(user=user))
 
# Admin routers
@router.message(Command("get_stats"), AdminFilter())
async def get_stats(message: types.Message) -> None:
    stats = get_user_statistics_text()
    await message.answer(stats)
    
@router.message(Command("send_weekly_report"), AdminFilter())
async def send_weekly_report(message: types.Message) -> None:
    await weekly_report()
    await message.answer("Weekly report sent.")
