import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from distance import get_grade, color_letter


def score_contact_loc(quality_locations, contact_loc):
    if contact_loc > quality_locations[0]:
        score = 0
    elif contact_loc > quality_locations[1]:
        score = 4
    elif contact_loc > quality_locations[2]:
        score = 3
    elif contact_loc > quality_locations[3]:
        score = 2
    else:
        score = 0
    return score


def timing_scorecard(quality_locations, timing_df):
    scorecard_list = []
    for batter in timing_df["batter"].unique():
        scorecard_dict = dict()
        scorecard_dict["batter"] = batter

        batter_df = timing_df[
            (timing_df["batter"] == batter) & (timing_df["contact_y_loc"] != 0.0)
        ].copy()

        swing_count = len(batter_df)
        if swing_count == 0:
            continue
        scorecard_dict["swing_count"] = swing_count
        batter_df["score"] = batter_df["contact_y_loc"].apply(
            lambda x: score_contact_loc(quality_locations, x)
        )
        contact_score_total = sum(batter_df["score"])
        contact_score_avg = contact_score_total / swing_count
        scorecard_dict["timing_avg"] = contact_score_avg
        timing_thresholds = {"A": 4, "B": 3, "C": 2, "D": 1}
        scorecard_dict["timing_grade"] = get_grade(contact_score_avg, timing_thresholds)
        scorecard_list.append(scorecard_dict)
    return pd.DataFrame.from_dict(scorecard_list)


def viz_contact_loc(batter_df, grade, quality_locations):

    font1 = {"size": 22}
    font2 = {"size": 18}
    font3 = {"size": 14}

    # Create figure and adjust size
    default_fig_size = (6.4, 4.8)
    size_adjust = 1.5
    larger_fig_size = [fig_size * size_adjust for fig_size in default_fig_size]
    fig, ax = plt.subplots(figsize=larger_fig_size)

    # Plot batter swing KDE
    if batter_df is not None:
        batter_id = batter_df["batter"].iloc[0]
        kde = sns.kdeplot(
            data=batter_df,
            x="contact_y_loc",
            multiple="stack",
            fill=True,
            bw_adjust=0.3,
            ax=ax,
        )

    # Get aspect ratio
    y_min = ax.get_ylim()[0]
    y_max = ax.get_ylim()[-1]
    x_min = min(ax.get_xlim()[0], -1.5)
    x_max = max(ax.get_xlim()[-1], 2)
    x_len = x_max - x_min
    y_one_foot = y_max / x_len
    y_mid = y_max / 2
    plt.xlim(x_min, x_max)

    # Draw home plate (simple representation)
    home_plate = plt.Polygon(
        [
            (0, -0.708 * y_one_foot + y_mid),
            (0, 0.708 * y_one_foot + y_mid),
            (-0.667, 0.708 * y_one_foot + y_mid),
            (-1.2, 0 + y_mid),
            (-0.667, -0.708 * y_one_foot + y_mid),
        ],
        color="gray",
        zorder=0.2,
    )
    ax.add_patch(home_plate)

    # Color the quality locations
    ranges = [
        (x_max, quality_locations[0]),
        (quality_locations[0], quality_locations[1]),
        (quality_locations[1], quality_locations[2]),
        (quality_locations[2], quality_locations[3]),
        (quality_locations[3], x_min),
    ]
    legend_patches = []
    zones = ["Other", "Home Run", "Line Drive", "Ground Ball", "Other"]
    zone_colors = ["red", "green", "blue", "orange", "red"]
    for i, range in enumerate(ranges):
        right = range[0] - 0.02
        left = range[1]
        width = right - left
        height = 10
        rect = Rectangle(
            (left, 0),
            width,
            height,
            fill=True,
            color=zone_colors[i],
            alpha=0.1,
            linewidth=3,
            linestyle="",
            zorder=0.1,
        )
        ax.add_patch(rect)
        legend_patches.append(rect)

    # Add two legends
    quality_legend = plt.legend(
        legend_patches[:-1],
        zones[:-1],
        loc="upper left",
        bbox_to_anchor=(1, 0.8),
        fontsize=font3["size"],
        title="Quality Locations",
        title_fontsize=font2["size"],
    )

    if batter_df is not None:
        ax.add_artist(quality_legend)
        kde_legend = plt.legend(
            [Line2D([0], [0], color="blue", lw=4)],
            ["Swing Frequency"],
            loc="upper left",
            bbox_to_anchor=(1, 1),
            fontsize=font3["size"],
            title="Swing Locations",
            title_fontsize=font2["size"],
        )

        plt.text(
            x_min + 0.1, y_min + 0.1, grade, fontsize=60, color=color_letter(grade)
        )
        subtitle = f"\n Batter: {batter_id}"
    else:
        subtitle = ""

    # Add titles and labels
    plt.title(f"Contact Location {subtitle}", font1)
    plt.xlabel("Contact Location (ft)", font2)
    plt.ylabel("Swing Frequencies", font2)

    plt.tight_layout(pad=3)
    return fig


if __name__ == "__main__":

    timing_metrics_df = pd.read_csv("../data/dataframes/timing_metrics_df.csv")
    qual_locs = [1.5, 0.9, 0.2, -0.5]
    timing_score_df = timing_scorecard(qual_locs, timing_metrics_df)

    batter_list = [849653732, 558675411]
    # when ready, create a list of all batters in scorecard_df and loop through
    # need to add code to save the resulting plots
    for batter_id in batter_list:
        batter_df = timing_metrics_df[
            (timing_metrics_df["batter"] == batter_id)
            & (timing_metrics_df["contact_y_loc"] != 0.0)
        ]
        grade = timing_score_df[timing_score_df["batter"] == batter_id][
            "timing_grade"
        ].values[0]
        fig = viz_contact_loc(batter_df, grade, qual_locs)
        plt.show()
        # plt.savefig(f'../images/grades/testing/rotated_{batter_id}_contact_location.png')

    widget_fig = viz_contact_loc(None, None, qual_locs)
    plt.show()
