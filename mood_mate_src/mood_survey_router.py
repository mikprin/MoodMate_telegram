# Moved here all the routes related to the mood survey
import time
import os
from aiogram import Router, F
from aiogram import types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from mood_mate_src.states_machine import AddRecord
from mood_mate_src.messaging.send import send_message_to_user
from mood_mate_src.database_tools.users import (
    User,
    UserSettings,
    Language,
    process_user_db,
    process_user_from_id,
)

from mood_mate_src.database_tools.mood_data import MoodRecord, MoodData, add_mood_record_to_db
from mood_mate_src.database_tools.redis_tools import (
    UserSession,
    create_user_session,
    get_user_session,
    get_today_session,
    save_user_session,
    remove_user_session,
)
from mood_mate_src.filters import ButtonTextFilter, MoodCallbackFilter, CallbackDataFilter
from mood_mate_src.mate_logger import logger
from mood_mate_src.keyboard import (
    get_all_buttons_text,
    BUTTONS_TEXT_LANG,
    emotional_emoji_sets,
    get_inline_keyboard_buttons_from_list,
    get_start_keyboard
)
from mood_mate_src.messaging.states_text import get_state_msg


def get_emoji_number_from_query(query: types.CallbackQuery) -> int:
    """Get the number from the emoji query"""
    return int(query.data.split('_')[1])

def validate_number_input(number: str) -> bool:
    """Validate if the input is a number"""
    try:
        num_f = float(number)
        if num_f < 0:
            return False
        return num_f
    except ValueError:
        return False


router = Router()

'''Order of the questions in the survey is as follows:

    - `mood` (int): mood of the user
    - `sleep` (int): hours of sleep
    - `energy` (int): energy level
    - `anxiety` (int): anxiety level
    - `exercise` (int): hours of exercise
    - `dopings` (str): list of dopings
    - `horny` (int): horny level
    - `period` (str): period  (optional)
    - `note` (str): note from the user
'''

@router.message(ButtonTextFilter(get_all_buttons_text("track_mood")))
async def track_mood_handler(message: Message, state: FSMContext):
    """Enter in AddRecord state handler
    Begins FSM related to adding a new MoodRecord
    Asks for the mood emoji selection
    """
    user = await process_user_db(message)
    
    session = create_user_session(user)
    await state.update_data(user=user)
    await state.set_state(AddRecord.mood)
    keyboard_buttons = emotional_emoji_sets["mood"].get_inline_keyboard_buttons()
    
    builder = InlineKeyboardBuilder()
    for button in keyboard_buttons:
        builder.add(button)
    await message.answer(f'{get_state_msg("mood", user)}\n{get_state_msg("emoji_explained", user)}', reply_markup=builder.as_markup())


@router.callback_query(MoodCallbackFilter())
async def mood_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Callback handler for mood emoji selection. Asks for the energy"""
    user = await process_user_from_id(query.from_user.id)
    number = get_emoji_number_from_query(query)
    await state.update_data(mood=number)
    session = get_user_session(user.user_id)
    session.mood_record.data.mood = number
    save_user_session(session)
    
    await state.set_state(AddRecord.sleep)
    await query.answer()
    await query.message.answer(f"{get_state_msg('sleep', user)}",
                                  reply_markup=types.ReplyKeyboardRemove())


@router.message(AddRecord.mood)
async def add_mood_handler(message: Message, state: FSMContext):
    """Add mood level to the state. In case of incorrect input, return to previous state"""
    user =  await process_user_db(message)
    # Save sleep here! # TODO
    await state.set_state(AddRecord.sleep)
    await message.answer(f"{get_state_msg('sleep', user)}\n{emotional_emoji_sets['energy'].get_comment(user.settings.language)}",
                         reply_markup=types.ReplyKeyboardRemove())

@router.message(AddRecord.sleep)
async def add_sleep_handler(message: Message, state: FSMContext):
    """Process the sleep input and
    go to the next `energy` state if the input is correct"""
    user = await process_user_db(message)
    
    sleep_result = validate_number_input(message.text)
    if sleep_result is not False:
        # await state.update_data(sleep=sleep_result)
        await state.set_state(AddRecord.horny)
        
        # Save data from sleep
        session = get_user_session(user.user_id)
        session.mood_record.data.sleep = sleep_result
        save_user_session(session)
        
        builder = emotional_emoji_sets["energy"].get_keyboard_builder()
        await message.answer(f"{get_state_msg('energy', user)}", reply_markup=builder.as_markup())
    else:
        # Return to previous state due to incorrect input
        await state.set_state(AddRecord.sleep)
        await message.answer(get_state_msg('invalid_number_input', user))


@router.callback_query(CallbackDataFilter(emotional_emoji_sets["energy"].data_type_names[0]))
async def energy_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Callback handler for energy emoji selection.
    Causes the anxiety level input"""
    user = await process_user_from_id(query.from_user.id)
    number = get_emoji_number_from_query(query)
    # await state.update_data(energy=number)
    session = get_user_session(user.user_id)
    session.mood_record.data.energy = number
    save_user_session(session)
    
    await state.set_state(AddRecord.exercise)
    await query.answer()
    
    builder = emotional_emoji_sets["anxiety"].get_keyboard_builder()
    await query.message.answer(f"{get_state_msg('anxiety', user)}",
                                  reply_markup=builder.as_markup())


@router.callback_query(CallbackDataFilter(emotional_emoji_sets["anxiety"].data_type_names[0]))
async def anxiety_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Callback handler for anxiety emoji selection and go to the exercise state"""
    user = await process_user_from_id(query.from_user.id)
    number = get_emoji_number_from_query(query)
    session = get_user_session(user.user_id)
    session.mood_record.data.anxiety = number
    save_user_session(session)
    
    await state.set_state(AddRecord.exercise)
    
    await query.answer(f"DEBUG: You entered: {number}")
    
    await query.message.answer(f"{get_state_msg('exercise', user)}",
                                  reply_markup=types.ReplyKeyboardRemove())


@router.message(AddRecord.exercise)
async def add_exercise_handler(message: Message, state: FSMContext):
    """Process the exercise input and go to the doping state"""
    user = await process_user_db(message)
    session = get_user_session(user.user_id)
    # Validate the input
    exercise_result = validate_number_input(message.text)
    if exercise_result is not False:
        await state.update_data(exercise=exercise_result)
        # Save exercise data
        session.mood_record.data.exercise = exercise_result
        save_user_session(session)
        await state.set_state(AddRecord.dopings)
        await message.answer(f"{get_state_msg('dopings', user)}")
        
        keyboard_buttons = get_inline_keyboard_buttons_from_list(user.settings.dopings_list, "dopings")
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await message.answer(f"{get_state_msg('dopings', user)}", reply_markup=keyboard)
    else:
        await state.set_state(AddRecord.exercise)
        await message.answer(get_state_msg('invalid_number_input', user))


@router.message(AddRecord.dopings)
async def add_dopings_handler(message: Message, state: FSMContext):
    """Process the doping input and listen for callbacks"""
    user = await process_user_db(message)
    session = get_user_session(user.user_id)
    dopings = user.settings.dopings_list
    keyboard_buttons = get_inline_keyboard_buttons_from_list(dopings, "dopings")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer(f"{get_state_msg('dopings', user)}", reply_markup=keyboard)


@router.callback_query(CallbackDataFilter("dopings"))
async def dopings_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Callback handler for doping selection"""
    user = await process_user_db(query)
    
    session = get_user_session(user.user_id)
    # logger.debug(f"User {user.user_id} picked: {query.data}")
    doping = query.data.split('_')[1]
    
    if doping == "accept":
        # In this case move to the next state
        # Dopings are already saved!
        save_user_session(session)
        await state.set_state(AddRecord.horny)
        await query.answer()
        builder = emotional_emoji_sets["horny"].get_keyboard_builder()
        await query.message.reply(f"{get_state_msg('horny', user)}", reply_markup=builder.as_markup())
    else:
        # Add or remove the doping from the list        
        all_dopings = user.settings.dopings_list
        checked_dopings = session.mood_record.data.dopings
        if doping in checked_dopings:
            checked_dopings.remove(doping)
        else:
            checked_dopings.append(doping)
        session.mood_record.data.dopings = checked_dopings
        save_user_session(session)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=get_inline_keyboard_buttons_from_list(all_dopings, "dopings", picked_options=checked_dopings))
        await query.message.edit_text(f"{get_state_msg('dopings', user)}", reply_markup=keyboard)


@router.callback_query(CallbackDataFilter(emotional_emoji_sets["horny"].data_type_names[0]))
async def horny_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Callback handler for horny emoji selection"""
    user = await process_user_from_id(query.from_user.id)
    number = get_emoji_number_from_query(query)
    session = get_user_session(user.user_id)
    session.mood_record.data.horny = number
    save_user_session(session)
    await state.set_state(AddRecord.future_in_years)
    await query.answer()
    # no_note inline keyboard
    await query.message.answer(f"{get_state_msg('future_in_years', user)}",
                                  reply_markup=types.ReplyKeyboardRemove())


@router.message(AddRecord.future_in_years)
async def add_futre_in_years_handler(message: Message, state: FSMContext):
    """Process the future in years input and save it to the state
    move to the note state"""
    user = await process_user_db(message)
    session = get_user_session(user.user_id)
    future_in_years = validate_number_input(message.text)
    if future_in_years is False:
        state.set_state(AddRecord.future_in_years)
        await message.answer(get_state_msg('invalid_number_input', user))
    else:
        # Go to the note state
        session.mood_record.data.future_in_years = future_in_years
        save_user_session(session)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=BUTTONS_TEXT_LANG[user.settings.language]["accept"], callback_data="no_note")],
            [types.InlineKeyboardButton(text=BUTTONS_TEXT_LANG[user.settings.language]["do_not_save"], callback_data="cancel_record")]
        ])
        await state.set_state(AddRecord.note)
        await message.answer(f"{get_state_msg('note', user)}", reply_markup=keyboard)

async def process_end_of_session(user: User, session: UserSession):
    """Process the end of the session
    Save it to DB and remove from cache"""
    
    session.mood_record.date = time.strftime("%Y.%m.%d")
    # TODO save the data to the DB
    await add_mood_record_to_db(session.mood_record)
    
    logger.debug(f"User {user.user_id} - {user.settings.username} saved the record: {session.mood_record.model_dump()}")
    remove_user_session(user.user_id)


@router.callback_query(CallbackDataFilter("no_note"))
async def no_note_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Process the note input and save the record. Also delete the session
    In case the user does not want to leave a note"""
    user = await process_user_from_id(query.from_user.id)
    session = get_user_session(user.user_id)
    
    await process_end_of_session(user, session)
    await state.clear()
    record = session.mood_record.model_dump()
    record_text = [f"{key}: {value}" for key, value in record.items()]
    record_text = "\n".join(record_text)
    if os.environ.get("DEBUG") == "True":
        await send_message_to_user(user.chat_id, f"Your record:\n{record_text}")
    await query.answer()
    await query.message.answer(f"{get_state_msg('record_saved', user)}", reply_markup=get_start_keyboard(user=user))

@router.callback_query(CallbackDataFilter("cancel_record"))
async def cancel_record_callback_handler(query: types.CallbackQuery, state: FSMContext):
    """Cancel the record and delete the session"""
    user = await process_user_from_id(query.from_user.id)
    session = get_user_session(user.user_id)
    remove_user_session(user.user_id)
    await state.clear()
    await query.answer()
    await query.message.answer(f"{get_state_msg('record_not_saved', user)}", reply_markup=get_start_keyboard(user=user))

@router.message(AddRecord.note)
async def add_note_handler(message: Message, state: FSMContext):
    """Process the note input and save the record. Also delete the session"""
    user = await process_user_db(message)
    session = get_user_session(user.user_id)
    
    session.mood_record.data.note = message.text
    await process_end_of_session(user, session)
    
    await state.clear()
    await message.answer(f"{get_state_msg('record_saved', user)}\nYour input is {session.mood_record.model_dump()}",
                         reply_markup=get_start_keyboard(user=user))