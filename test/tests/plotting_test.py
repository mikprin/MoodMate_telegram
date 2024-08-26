import sys, os
import pandas as pd

from mood_mate_src.analytics.plotting import get_plot_from_df



def test_get_plot_from_df():
    
    data_path = f"{sys.path[0]}/../resources/example_csv_data/records.csv"
    
    print(data_path)
    assert os.path.exists(data_path)
    
    df = pd.read_csv(data_path)
    
    get_plot_from_df(df, "test_plot.png")
    
    assert os.path.exists("test_plot.png")
    
    os.remove("test_plot.png")