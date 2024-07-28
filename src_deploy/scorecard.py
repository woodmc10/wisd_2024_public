import pandas as pd
from swing_map import swing_map_scorecard
from attack_angle import create_tracking_score_df
from timing_rotate import timing_scorecard


def merge_metrics(data_folder):
    """
    Merge various metrics into one DataFrame.

    Args:
        data_folder (str): Path to the folder containing metric data files.

    Returns:
        pd.DataFrame: Merged DataFrame containing all metrics.
    """
    # import all data
    swing_map_df = pd.read_csv(f"{data_folder}/swing_map_metrics_df.csv")
    distance_metrics_df = pd.read_csv(f"{data_folder}/distance_metrics_df.csv")
    tracking_metrics_df = pd.read_csv(f"{data_folder}/tracking_metrics_df.csv")
    timing_metrics_df = pd.read_csv(f"{data_folder}/timing_metrics_df.csv")

    # merge all metrics to one dataframe
    all_metrics_df = (
        swing_map_df.merge(
            distance_metrics_df[["batter", "batter_count", "distance"]],
            on=["batter", "batter_count"],
            how="outer",
        )
        .merge(
            tracking_metrics_df[
                ["batter", "batter_count", "attack_angle", "track_angle"]
            ],
            on=["batter", "batter_count"],
            how="outer",
        )
        .merge(
            timing_metrics_df[["batter", "batter_count", "contact_y_loc"]],
            on=["batter", "batter_count"],
            how="outer",
        )
        .drop("Unnamed: 0", axis=1)
        .dropna(subset=["batter"])
    )

    return all_metrics_df


def generate_scorecard(
    data_folder, contact_location_values, track_angle_values, hunting_values
):
    """
    Generate a scorecard by merging and scoring all swing metrics.

    Args:
        data_folder (str): Path to the folder containing metric data files.
        contact_location_values (list): Custom values for contact location scoring.
        track_angle_values (list): Custom values for track angle scoring.
        hunting_values (list): Custom values for swing map (hunting) scoring.

    Returns:
        pd.DataFrame: DataFrame containing the scorecard.
    """
    # get all metrics for each swing
    all_swing_metrics_df = merge_metrics(data_folder)
    # get summary metrics for each batter
    timing_score_df = timing_scorecard(contact_location_values, all_swing_metrics_df)
    tracking_score_df = create_tracking_score_df(
        track_angle_values, all_swing_metrics_df
    )
    hunting_score_df = swing_map_scorecard(hunting_values, all_swing_metrics_df)
    # merge all metrics into a scorecard
    scorecard_df = timing_score_df.merge(
        tracking_score_df, on="batter", how="outer"
    ).merge(hunting_score_df, on="batter", how="outer")

    return scorecard_df


if __name__ == "__main__":
    data_folder = "../data/dataframes/"

    contact_location_defaults = [1.5, 0.9, 0.2, -0.5]
    track_angle_defaults = [5, 5, 10, 15]
    hunting_defaults = [1.5, 2.0, 2.5, 3.0]
    scorecard_df = generate_scorecard(
        data_folder, contact_location_defaults, track_angle_defaults, hunting_defaults
    )
    scorecard_df.to_csv(f"{data_folder}scorecard.csv")
