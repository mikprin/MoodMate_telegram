import pandas as pd

from mood_mate_src.database_tools.mood_data import (
    MoodData, MoodRecord, get_mood_records_from_db,
    get_user_records_for_past_time)


def flatten_record(record: MoodRecord) -> dict:
    """Output a dictionary with all the data from a MoodRecord object flattened into a single dictionary.
    Separating MoodData field from other fields."""
    record_dict = record.model_dump()
    # Flatten data into record_dict
    return_dict = dict()
    return_dict.update(record_dict)
    return_dict.update(record_dict['data'])
    return_dict.pop('data')
    return return_dict

def convert_records_to_pandas(records: list[MoodRecord]) -> pd.DataFrame:
    """Convert a list of MoodRecord objects into a pandas DataFrame."""
    flatten_records = []
    for record in records:
        flatten_records.append(flatten_record(record))
    return pd.DataFrame(flatten_records)


def get_user_pandas_df(user_id: int, time_period: int | None = None ) -> pd.DataFrame:
    """Get a pandas DataFrame with all the mood records for a given user_id.
    Don't forget to check it it's empty or not!"""
    if time_period is not None:
        records = get_user_records_for_past_time(user_id, time_period)
    else:
        records = get_mood_records_from_db(user_id)
    return convert_records_to_pandas(records)
