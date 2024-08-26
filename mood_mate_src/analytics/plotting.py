import pandas as pd
import matplotlib.pyplot as plt

import datetime

from mood_mate_src.database_tools.schema import Language

# Applying the dark background style
# plt.style.use('dark_background')

NUMERIC_VALUES = ['mood', 'energy', 'future_in_years', 'exercise', 'anxiety']

axis_names = {
    
    Language.ENG.value: {
        'mood': 'Mood',
        'energy': 'Energy',
        'future_in_years': 'Future in Years',
        'exercise': 'Exercise',
        'anxiety': 'Anxiety',
        'sleep': 'Sleep',
        'over_time': 'Over Time',
        'created_at': 'Created At'
    },
    
    Language.RU.value: {
        'mood': 'Настроение',
        'energy': 'Энергия',
        'future_in_years': 'Будущее в годах',
        'exercise': 'Тренировки',
        'anxiety': 'Тревога',
        'sleep': 'Сон',
        'over_time': 'от времени',
        'created_at': 'Время записи'
    }
}

def over_time_it(metric: str, language: str = Language.ENG.value) -> str:
    return f"{axis_names[language][metric]} {axis_names[language]['over_time']}"

def get_plot_from_df(df: pd.DataFrame, save_path: str, language: str = Language.ENG.value) -> None:
    
    # df = df[NUMERIC_VALUES + ['created_at']]
    
    if df.shape[0] == 0:
        return False
    
    # Assuming df is your DataFrame with columns including 'created_at'
    df['created_at'] = pd.to_datetime(df['created_at'], unit='s')
        
    numbers_map = {
        "mood": 0,
        "energy": 1,
        "sleep": 1,
        "future_in_years": 4,
        "exercise": 2,
        "anxiety": 3
    }

    # Define colors
    # background_color = "#2C5266"
    background_color = "#214152"
    colors = {
        'mood': '#439a86',
        'energy': '#bcd8c1',
        'future_in_years': '#e9d985',
        'exercise': '#DBD5B2',
        'anxiety': '#f03a47',
        'sleep': '#65C1F3',
    }
    

    # line_colors = ['#' + color for color in line_colors]
    line_width = 2.5  # Thicker lines

    # Apply custom style
    plt.style.use('dark_background')
    plt.rcParams.update({
        'axes.facecolor': background_color,
        'figure.facecolor': background_color,
        'axes.edgecolor': 'white',
        'axes.grid': True,
        'grid.color': '#666666',
        'grid.alpha': 0.5,
        'text.color': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white'
    })

    # Setting up subplots
    fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(10, 12), sharex=True)

    # Plotting each variable with custom colors
    axes[numbers_map['mood']].plot(df['created_at'], df['mood'], color=colors['mood'], linewidth=line_width)
    axes[numbers_map['mood']].set_ylabel(f'{axis_names[language]["mood"]}')
    axes[numbers_map['mood']].set_title(f'{over_time_it("mood", language=language)}', color='white')

    axes[numbers_map['energy']].plot(df['created_at'], df['energy']*2, color=colors['energy'], linewidth=line_width, label=axis_names[language]['energy'])
    axes[numbers_map['sleep']].plot(df['created_at'], df['sleep'], color=colors['sleep'], linewidth=line_width, label=axis_names[language]['sleep'])
    axes[numbers_map['energy']].set_ylabel(f'{axis_names[language]["energy"]} & {axis_names[language]["sleep"]}')
    axes[numbers_map['energy']].set_title(f'{axis_names[language]["sleep"]} & {over_time_it("energy", language=language)}', color='white')
    axes[numbers_map['energy']].legend(loc='upper left')

    axes[numbers_map['future_in_years']].plot(df['created_at'], df['future_in_years'], color=colors['future_in_years'], linewidth=line_width)
    axes[numbers_map['future_in_years']].set_ylabel(f'{axis_names[language]["future_in_years"]}')
    axes[numbers_map['future_in_years']].set_title(f'{over_time_it("future_in_years", language=language)}', color='white')

    axes[numbers_map['exercise']].plot(df['created_at'], df['exercise'], color=colors['exercise'], linewidth=line_width)
    axes[numbers_map['exercise']].set_ylabel(f'Exercise')
    axes[numbers_map['exercise']].set_title(f'{over_time_it("exercise", language=language)}', color='white')

    axes[numbers_map['anxiety']].plot(df['created_at'], df['anxiety'], color=colors['anxiety'], linewidth=line_width)
    axes[numbers_map['anxiety']].set_ylabel(f'{axis_names[language]["anxiety"]}')
    axes[numbers_map['anxiety']].set_title(f'{over_time_it("anxiety", language=language)}', color='white')
    axes[4].set_xlabel(f'{axis_names[language]["created_at"]}')

    # Save to file
    fig.patch.set_facecolor(background_color)
    fig.savefig(save_path, dpi=400, bbox_inches='tight', facecolor=background_color)
    
    return True