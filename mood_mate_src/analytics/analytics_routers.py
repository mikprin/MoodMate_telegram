# Moved here all the routes related to the mood survey
import os
import tempfile
from aiogram import Router, F
from aiogram import types
from aiogram.types import InlineKeyboardButton, Message, BufferedInputFile, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from mood_mate_src.messaging.states_text import get_state_msg
from mood_mate_src.filters import ButtonTextFilter, CallbackDataFilter
from mood_mate_src.database_tools.users import (
    User,
    UserSettings,
    Language,
    process_user_db,
    process_user_from_id
)
from mood_mate_src.keyboard import (
    get_all_buttons_text,
    BUTTONS_TEXT_LANG,
    emotional_emoji_sets,
    get_inline_keyboard_buttons_from_list,
    get_start_keyboard
)
from mood_mate_src.mate_logger import logger
from mood_mate_src.analytics.convert import get_user_pandas_df
from mood_mate_src.messaging.send import send_file_to_user
from mood_mate_src.analytics.plotting import get_plot_from_df

router = Router()


@router.message(ButtonTextFilter(get_all_buttons_text("mood_data")))
async def track_mood_handler(message: Message, state: FSMContext):
    """Enter in AddRecord state handler
    Begins FSM related to adding a new MoodRecord
    Asks for the mood emoji selection
    """
    user = await process_user_db(message)
    language = user.settings.language
    
    keyboard = types.InlineKeyboardMarkup(
        # row_width=4,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["get_csv"],
                                    callback_data="get_csv")
            ],
            [
                InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["get_plot"],
                                     callback_data="get_plot_all"),
            ]
            # [
            #     InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["toggle_reminder"],
            #                         callback_data="toggle_reminder"),
            # ],
        ]
    )
    await message.answer(BUTTONS_TEXT_LANG[language]["mood_data"], reply_markup=keyboard)


@router.callback_query(CallbackDataFilter("get_csv"))
async def get_csv_handler(call: types.CallbackQuery):
    """Get the CSV file with the mood records"""
    user = await process_user_from_id(call.from_user.id)
    logger.info(f"User {user.settings.username} requested the CSV file")
    # Get the CSV file
    df = get_user_pandas_df(user.user_id)
    # Get tempdir path
    with tempfile.TemporaryDirectory() as tempdir:
        file_name = f"{user.user_id}_records.csv"
        csv_path = os.path.join(tempdir, file_name)
        df.to_csv(csv_path, index=False)
        await call.answer("CSV file is ready!")
        # await send_file_to_user(user.chat_id, csv_path)
        await call.message.answer_document(FSInputFile(csv_path))
        # Remove the file
        os.remove(csv_path)
        logger.info(f"CSV file sent to user {user.settings.username}")
        

@router.callback_query(CallbackDataFilter("get_plot_all"))
async def get_plot_all_handler(call: types.CallbackQuery):
    """Get the plot with the mood records"""
    user = await process_user_from_id(call.from_user.id)
    logger.info(f"User {user.settings.username} requested the plot")
    # Get the CSV file
    df = get_user_pandas_df(user.user_id)
    
    if df.shape[0] < 2:
        await call.answer()
        await call.message.answer(get_state_msg("not_enough_records", user))
    else:
        # Get tempdir path
        with tempfile.TemporaryDirectory() as tempdir:
            file_name = f"{user.user_id}_plot.png"
            plot_path = os.path.join(tempdir, file_name)
            get_plot_from_df(df, plot_path, language=user.settings.language)
            await call.answer()
            await call.message.answer_photo(FSInputFile(plot_path))
            # Remove the file
            os.remove(plot_path)
            logger.info(f"Plot sent to user {user.settings.username}")