import pandas as pd

from mood_mate_src.analytics.convert import convert_records_to_pandas
from mood_mate_src.database_tools.mood_data import \
    get_all_records_for_past_time
from mood_mate_src.database_tools.users import get_all_users_from_db


def get_user_statistics_text() -> str:
    users = get_all_users_from_db()
    # Header
    stats = "User statistics\n"
    stats = f"Total users: {len(users)}\n"
    # Activity for the last 7 days
    delta = 60*60*24*7
    records = get_all_records_for_past_time(delta)
    df : pd.DataFrame = convert_records_to_pandas(records)
    unique_weekly_users = df['user_id'].unique()
    stats += f"Total records for the last 7 days: {len(records)}\n"
    stats += f"Unique users for the last 7 days: {len(unique_weekly_users)}\n"
    return stats
