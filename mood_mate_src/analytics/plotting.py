import os
import numpy as np
import pandas as pd
import emoji
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from scipy.interpolate import interp1d
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import mood_mate_src.resources as resources_path
import importlib.resources as pkg_resources
from mood_mate_src.mate_logger import logger

# Use the Noto Sans Symbols2 font or Noto Color Emoji for emojis
# plt.rcParams['font.family'] = 'Noto Sans Symbols2'

# Some magic to make it work faster
if os.environ.get('USE_OPTIMIZED_PLOTTING', None) == 'True':
    matplotlib.use('Agg')

from mood_mate_src.database_tools.schema import Language, User, UserSettings
from mood_mate_src.keyboard import emotional_emoji_sets

# Applying the dark background style
# plt.style.use('dark_background')

NUMERIC_VALUES = ['mood', 'energy', 'future_in_years', 'exercise', 'anxiety']


def get_emoji_limits(set: str) -> tuple:
    emotional_emoji_sets[set]
    return (0, len(emotional_emoji_sets[set].emoji_set) - 1)

def smooth_line(x, y, kind='cubic', num_points=500):
    x_new = np.linspace(x.min(), x.max(), num_points)
    f = interp1d(x, y, kind=kind)
    y_smooth = f(x_new)
    return x_new, y_smooth

def smooth_line_for_x(x, y, kind='cubic', num_points=500):
    """Like `smooth_line` but if x already has the right values"""
    f = interp1d(x, y, kind=kind)
    y_smooth = f(x)
    return y_smooth


def find_emojis_in_string(string: str) -> list:
    """Find all emojis in a string."""
    return [char for char in string if char in emoji.EMOJI_DATA]


def find_emojis_in_list(list_: list) -> list:
    """Find all emojis in a list of strings."""
    return [find_emojis_in_string(string) for string in list_]


def get_list_from_string_or_list(string_or_list) -> list:
    """Convert a string representation of a list into a list."""
    if isinstance(string_or_list, list):
        return string_or_list
    else:
        return eval(string_or_list)

axis_names = {
    
    Language.ENG.value: {
        'mood': 'Mood',
        'energy': 'Energy',
        'future_in_years': 'Future in Years',
        'exercise': 'Exercise',
        'anxiety': 'Anxiety',
        'sleep': 'Sleep',
        'horny': 'Horny',
        'over_time': 'Over Time',
        'created_at': 'Created At',
        'recommended_sleep': 'Recommended Sleep'
    },
    
    Language.RU.value: {
        'mood': 'Настроение',
        'energy': 'Энергия',
        'future_in_years': 'Будущее в годах',
        'exercise': 'Тренировки',
        'anxiety': 'Тревога',
        'sleep': 'Сон',
        'horny': 'Возбужденность',
        'over_time': 'от времени',
        'created_at': 'Время записи',
        'recommended_sleep': 'Рекомендуемый сон'
    }
}

temporary_images_map = {
    Language.ENG.value: {
                        "Coffee/caffeine: ☕" : 'coffe.png',
                        "Coffee ☕" : 'coffe.png',
                        "Sugar 🍬" : 'sweets.png',
                        "Sugar: 🍬" : 'sweets.png',
                        "Smoking: 🚬" : 'smoking.png',
                        "Alcohol: 🍺 or 🍷" : 'alcohol.png',
                        "Weed: 🌿" : 'weed.png',
                        "Mushrooms: 🍄" : 'mushrooms.png',
                        # "LSD: 🌈" : 'lsd.png',
                        "Pills?: 💊" : 'pills.png',
                        "Vitamins/Supplements: 🍊" : 'vitamins.png',
                        "Zap: ⚡" : 'zap.png',
                        "Gaming: 🎮": 'video_game.png',
    },
    Language.RU.value: {
                        "Кофе/кофеин: ☕" : 'coffe.png',
                        "Кофе ☕" : 'coffe.png',
                        "Сахар 🍬" : 'sweets.png',
                        "Сахар: 🍬" : 'sweets.png',
                        "Курение: 🚬" : 'smoking.png',
                        "Алкоголь: 🍺 или 🍷" : 'alcohol.png',
                        "Трава: 🌿" : 'weed.png',
                        "Грибы: 🍄" : 'mushrooms.png',
                        # "ЛСД: 🌈" : 'lsd.png',
                        "Таблетки?: 💊" : 'pills.png',
                        "Витамины/БАД: 🍊" : 'vitamins.png',
                        "Зап: ⚡" : 'zap.png',
                        "Игры: 🎮" : 'video_game.png',
    }
}

def over_time_it(metric: str, language: str = Language.ENG.value) -> str:
    return f"{axis_names[language][metric]} {axis_names[language]['over_time']}"

def get_plot_from_df(df: pd.DataFrame,
                     save_path: str,
                     language: str = Language.ENG.value,
                     user: User | None = None,
                     interpolate=False,
                     ) -> None:
    """Plot the mood data from the DataFrame and save it to the file

    Args:
        df (pd.DataFrame): DataFrame with mood data
        save_path (str): path to save the plot
        language (str, optional): _description_. Defaults to Language.ENG.value.

    Returns:
        True: if the plot was saved successfully
        False: if the DataFrame is empty or some other error occurred
    """
    
    
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
    
    # Plot horny with color map based on its level
    # Normalize the horny data to fit into the colormap range [0, 1]
    (horny_min, horny_max) = get_emoji_limits('horny')

    horny_normalized = (df['horny'] - horny_min) / (horny_max - horny_min)
    # Create a colormap from green to red
    cmap = cm.get_cmap('RdYlGn_r')

    # Check if sleep level is needed to be plotted
    if user is not None and user.settings.recommended_sleep is not None:
        recommended_sleep = user.settings.recommended_sleep
    else:
        recommended_sleep = None

    # prepare to add dopings icons to the plot:
    dopings = df[df.dopings.apply(lambda x: len(get_list_from_string_or_list(x)) > 0)][['dopings', 'created_at', 'mood']]
    
    # Add images column to the dopings dataframe as empty lists
    dopings['images'] = [list() for _ in range(len(dopings))]
    
    
    # dopings['emojis'] = dopings.dopings.apply(lambda x: find_emojis_in_list(x))
    # Now I have a DataFrame with only rows that have dopings
    if dopings.shape[0] > 0:
        # For each row in dopings dataframe check if there are element with key in temporary_images_map and if so add the image path to the row to the images column
        for language, images_map in temporary_images_map.items():
            for key, value in images_map.items():
                dopings.loc[dopings.dopings.apply(lambda x: key in x), 'images'] = dopings.loc[dopings.dopings.apply(lambda x: key in x), 'images'].apply(lambda x: x + [value])
    else:
        dopings = None

    # Setting up subplots
    fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(10, 12), sharex=True)
    
    # Plotting each variable with custom colors
    # Mood
    # axes[numbers_map['mood']].plot(df['created_at'], df['mood'], color=colors['mood'], linewidth=line_width)
    
    # Plotting mood and overlaying horny as a colormap
    axes[numbers_map['mood']].plot(df['created_at'], df['mood'], color=colors['mood'], linewidth=line_width)
    for i in range(len(df) - 1):
        axes[numbers_map['mood']].plot(
            df['created_at'].iloc[i:i+2],
            df['mood'].iloc[i:i+2],
            color=cmap(horny_normalized.iloc[i]),
            linewidth=line_width + 0.8  # Make the colormap line slightly thicker
        )
    
    
    # COLOR BAR NOT WORKING
    # Create a colorbar for horny
    # horny_colorbar = cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=horny_min, vmax=horny_max))
    # horny_colorbar.set_array([])
    # fig.colorbar(horny_colorbar,
    #             #  ax=axes[numbers_map['mood']],
    #             ax = axes[0],
    #              orientation='vertical',
    #              pad=0.01)
    # axes[numbers_map['mood']].set_xlabel('')
    
    axes[numbers_map['mood']].set_ylabel(f'{axis_names[language]["mood"]}')
    axes[numbers_map['mood']].set_ylim(get_emoji_limits('mood'))
    axes[numbers_map['mood']].set_title(f'{over_time_it("mood", language=language)}', color='white')

    # Add emojis to the mood plot
    if dopings is not None:
        
        with pkg_resources.path(resources_path, 'pictograms') as img_path:
            # img_path is a pathlib.Path object, which is an absolute path
            pictogram_folder = img_path.resolve()
            # print(f"Absolute path: {absolute_path}")
        
        for idx, row in dopings.iterrows():
            if row['images']:  # Check if there are images to plot
                # If the mood is high, the images should be plotted below the mood line
                # To not go out of the plot, the offset should be negative
                if row['mood'] > 4:
                    offset_diff = -1
                else:
                    offset_diff = 1
                offset_y = 0
                for image_file in row['images']:
                    image_path = os.path.join(pictogram_folder, image_file)
                    if os.path.exists(image_path):  # Check if the file exists
                        image = plt.imread(image_path)  # Read the image
                        imagebox = OffsetImage(image, zoom=0.15)  # Adjust zoom level to fit the image size
                        ab = AnnotationBbox(imagebox, (row['created_at'], row['mood'] + offset_y),
                                            frameon=False, box_alignment=(0.5, 0.5))
                        axes[numbers_map['mood']].add_artist(ab)
                    else:
                        logger.error(f"Image file {image_path} not found during plotting")
                    # Add offset equal to the width of the image
                    offset_y += offset_diff

    # Energy and Sleep
    axes[numbers_map['energy']].plot(df['created_at'], df['energy']*2, color=colors['energy'], linewidth=line_width, label=axis_names[language]['energy'])
    axes[numbers_map['sleep']].plot(df['created_at'], df['sleep'], color=colors['sleep'], linewidth=line_width, label=axis_names[language]['sleep'])
    if recommended_sleep is not None:
        # Optional recommended sleep part
        axes[numbers_map['sleep']].axhline(y=recommended_sleep, color='white', linestyle='--', linewidth=1, label=f'{axis_names[language]["recommended_sleep"]} {recommended_sleep}h')
    
    axes[numbers_map['energy']].set_ylabel(f'{axis_names[language]["energy"]} & {axis_names[language]["sleep"]}')
    axes[numbers_map['energy']].set_title(f'{axis_names[language]["sleep"]} & {over_time_it("energy", language=language)}', color='white')
    axes[numbers_map['energy']].legend(loc='lower left')

    axes[numbers_map['future_in_years']].plot(df['created_at'], df['future_in_years'], color=colors['future_in_years'], linewidth=line_width)
    axes[numbers_map['future_in_years']].set_ylabel(f'{axis_names[language]["future_in_years"]}')
    
    if df['future_in_years'].max() / (df['future_in_years'].min() + 0.1) > 10:  # If the range is too big for linear scale - use log scale
        axes[numbers_map['future_in_years']].set_yscale('log')
    
    axes[numbers_map['future_in_years']].set_title(f'{over_time_it("future_in_years", language=language)}', color='white')

    axes[numbers_map['exercise']].plot(df['created_at'], df['exercise'], color=colors['exercise'], linewidth=line_width)
    axes[numbers_map['exercise']].set_ylabel(f'{axis_names[language]["exercise"]}')
    axes[numbers_map['exercise']].set_title(f'{over_time_it("exercise", language=language)}', color='white')

    axes[numbers_map['anxiety']].plot(df['created_at'], df['anxiety'], color=colors['anxiety'], linewidth=line_width)
    axes[numbers_map['anxiety']].set_ylabel(f'{axis_names[language]["anxiety"]}')
    axes[numbers_map['anxiety']].set_ylim(get_emoji_limits('anxiety'))
    axes[numbers_map['anxiety']].set_title(f'{over_time_it("anxiety", language=language)}', color='white')
    axes[4].set_xlabel(f'{axis_names[language]["created_at"]}')

    # Save to file
    fig.patch.set_facecolor(background_color)
    fig.savefig(save_path, dpi=400, bbox_inches='tight', facecolor=background_color)
    
    return True