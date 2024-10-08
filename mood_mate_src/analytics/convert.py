import pandas as pd
from mood_mate_src.database_tools.mood_data import MoodRecord, MoodData, get_mood_records_from_db

def flatten_record(record: MoodRecord) -> dict:
    """Output a dictionary with all the data from a MoodRecord object flattened into a single dictionary."""
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


def get_user_pandas_df(user_id: int) -> pd.DataFrame:
    """Get a pandas DataFrame with all the mood records for a given user_id."""
    records = get_mood_records_from_db(user_id)
    return convert_records_to_pandas(records)