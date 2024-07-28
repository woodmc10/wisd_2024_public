import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import get_grade, color_letter


def filter_path(path_df):
    """
    Filter the path DataFrame to include rows around the 'Hit' or 'Nearest' event.

    Args:
        path_df (pd.DataFrame): The path DataFrame containing event data.

    Returns:
        pd.DataFrame: Filtered DataFrame including rows 50 before and 50 after the
        'Hit' or 'Nearest' event.
    """
    mid_index = path_df.index[path_df.event.isin(["Hit", "Nearest"])].to_list()
    start_index = mid_index[0] - 50
    end_index = mid_index[0] + 50
    return path_df[start_index:end_index]


def normalize_path(path):
    """
    Normalize the path coordinates to start from the initial position and correct for
    negative handle positions.

    Args:
        path (pd.DataFrame): The path DataFrame containing positional data.

    Returns:
        pd.DataFrame: Normalized DataFrame with corrected positional data.
    """
    # mirror swings starting at a negative position to normalize for switch hitters
    if path["handle_pos_0"].iloc[0] < 0:
        path["head_pos_0"] = path["head_pos_0"] * -1
        path["handle_pos_0"] = path["handle_pos_0"] * -1

    pos_columns = [
        "head_pos_0",
        "head_pos_1",
        "head_pos_2",
        "handle_pos_0",
        "handle_pos_1",
        "handle_pos_2",
    ]
    return path[pos_columns] - path[pos_columns].iloc[0]


def combine_coordinates(df):
    """
    Combine head and handle positional coordinates into a single numpy array for
    distance time warp analysis.

    Args:
        df (pd.DataFrame): The DataFrame containing positional data.

    Returns:
        np.ndarray: Combined array of positional coordinates.
    """
    return df[
        [
            "head_pos_0",
            "head_pos_1",
            "head_pos_2",
            "handle_pos_0",
            "handle_pos_1",
            "handle_pos_2",
        ]
    ].values



def convert_column_name(column_name):
    """
    Convert a column name to a more readable format.

    Args:
        column_name (str): The original column name.

    Returns:
        str: The converted column name.
    """
    # should this be moved to a utils file?
    bat_section = column_name.split("_")[0].capitalize()
    axes_list = ["X", "Y", "Z"]
    letter = axes_list[int(column_name.split("_")[-1])]
    return f"{bat_section} {letter}"



def similarity_scorecard(dist_grades, distance_df):
    """
    Generate a scorecard for batters based on their distance metrics.

    Args:
        dist_grades (list): List of distance thresholds for grading.
        distance_df (pd.DataFrame): DataFrame containing distance metrics.

    Returns:
        pd.DataFrame: Scorecard DataFrame for each batter.
    """
    batters = distance_df.batter.unique()
    scorecard_list = []
    for batter in batters:
        scorecard_dict = dict()
        scorecard_dict["batter"] = batter
        
        batter_df = distance_df[
            (distance_df["batter"] == batter) & (distance_df["distance"] > 0)
        ]
        # distance values of -2, -1, and 0 indicate specific data situations, and should not
        # be included in the variance calculations
        if len(batter_df) == 0:
            continue
        # use mean +/- 2 std to find outlier swings
        min_dist = np.mean(batter_df["distance"]) - 2 * np.std(batter_df["distance"])
        max_dist = np.mean(batter_df["distance"]) + 2 * np.std(batter_df["distance"])
        swing_count = len(batter_df)
        good_count = len(
            batter_df[
                (batter_df["distance"] < max_dist) & (batter_df["distance"] > min_dist)
            ]
        )
        scorecard_dict["dist_score"] = good_count / swing_count
        # convert good swing percent (dist_score) to a grade
        distance_thresholds = {
            "A": dist_grades[0],
            "B": dist_grades[1],
            "C": dist_grades[2],
            "D": dist_grades[3],
        }
        scorecard_dict["dist_grade"] = get_grade(
            good_count / swing_count, distance_thresholds
        )
        scorecard_list.append(scorecard_dict)
    return pd.DataFrame.from_dict(scorecard_list)


if __name__ == "__main__":

    distance_metrics_df = pd.read_csv("../data/dataframes/distance_metrics_df.csv")

    dist_defaults = [1.0, 0.95, 0.9, 0.85]
    scorecard_df = similarity_scorecard(dist_defaults, distance_metrics_df)
    batter_list = [223971350]
