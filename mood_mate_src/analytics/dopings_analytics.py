import pandas as pd

from mood_mate_src.analytics.convert import convert_records_to_pandas
from mood_mate_src.database_tools.mood_data import MoodRecord
from mood_mate_src.database_tools.schema import User


def get_dopings_monthly_summary(df: pd.DataFrame, user: User) -> str:

    # Convert to datetime for monthly grouping
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")  # Year-Month format

    # Create a list of all dopings
    all_dopings = df["dopings"].explode().dropna().unique()

    # # Create a new DataFrame with the counts of each doping for each month
    # monthly_counts = df.groupby([df["date"].dt.strftime("%Y-%m"), "dopings"]).size().unstack().fillna(0)

    monthly_counts = (
        df.explode("dopings").groupby(["month", "dopings"]).size().unstack(fill_value=0)
    )
    # Generate the monthly summary
    summary = generate_monthly_summary(monthly_counts, user)
    return summary


def generate_monthly_summary(monthly_counts, user: User) -> str:
    if user.settings.language == "ru":
        summary = "<b>Ежемесячная сводка по отметкам о допингах:</b>\n"
    else:
        summary = "<b>Monthly Summary of Dopings:</b>\n"

    for month in monthly_counts.index:
        summary += f"\n📅 <b>{month}:</b>\n"
        for doping, count in monthly_counts.loc[month].items():
            if count != 0:
                summary += f"- {doping}: {count}\n"
    return summary
