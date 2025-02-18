import os
import sys

import pandas as pd
import pytest

from mood_mate_src.analytics.plotting import get_plot_from_df


@pytest.fixture
def df_records():
    data_path = f"{sys.path[0]}/../resources/example_csv_data/records.csv"
    return pd.read_csv(data_path)

def test_get_plot_from_df(df_records):
    get_plot_from_df(df_records, "test_plot.png")
    assert os.path.exists("test_plot.png")
    os.remove("test_plot.png")

def test_plot_with_with_empty_row(df_records):
    """Test the function with a DataFrame that has an empty row will not raise an error.
    Used for diary records"""
    df_records = pd.concat([df_records, pd.Series()], ignore_index=True)

    df_records = pd.concat([df_records, pd.Series([None] * len(df_records.columns), index=df_records.columns, dtype='object').to_frame().T], ignore_index=True)
    df_records.at[len(df_records) - 1, 'note'] = "NOTE"
    # Add the created_at and date columns
    df_records.at[len(df_records) - 1, 'created_at'] = 1735660800
    df_records.at[len(df_records) - 1, 'date'] = '2024.12.31'
    # Dopings are an empty list
    df_records.at[len(df_records) - 1, 'dopings'] = []
    get_plot_from_df(df_records, "test_plot.png")
    assert os.path.exists("test_plot.png")
    os.remove("test_plot.png")
