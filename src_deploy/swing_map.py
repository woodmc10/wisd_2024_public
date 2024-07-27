import math
import pandas as pd
from itertools import combinations
import seaborn as sns
import numpy as np
from matplotlib import patches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from attack_angle import get_ball_contact_idx
from distance import get_grade, color_letter

def geometric_median(df, epsilon=1e-5):
    """
    Computes the geometric median of a set of points using Weiszfeld's algorithm.
    
    :param df: A pandas DataFrame with columns 'x' and 'y' representing the points.
    :param epsilon: A small threshold to stop the iteration.
    :return: A tuple containing the geometric median (x_m, y_m) and a list of distances to each point.
    """
    points = df[['pitch_x', 'pitch_z']].to_numpy()
    median = np.mean(points, axis=0)  # Initial guess: centroid

    while True:
        distances = np.linalg.norm(points - median, axis=1)
        nonzero_distances = distances != 0
        distances = np.where(nonzero_distances, distances, np.inf)
        weighted_sum = np.sum(points / distances[:, np.newaxis], axis=0)
        new_median = weighted_sum / np.sum(1 / distances)
        
        if np.linalg.norm(new_median - median) < epsilon:
            break
        
        median = new_median

    # Compute final distances to the geometric median
    final_distances = np.linalg.norm(points - median, axis=1)
    
    return median, final_distances


def pitch_location(ball_df, bat_df):
    ball_df_dedup = ball_df.drop_duplicates().reset_index()
    hit_frame = bat_df[bat_df['event'].isin(['Hit', 'Nearest'])]
    contact_time = hit_frame['time'].values[0]
    contact_idx = get_ball_contact_idx(ball_df_dedup, contact_time)
    contact_row = ball_df_dedup.loc[contact_idx, :]
    pitch_x = contact_row['pos_0']
    pitch_z = contact_row['pos_2']
    return pitch_x, pitch_z

def swing_outcome(json_file):
    result = json_file['summary_acts']['pitch']['result']
        # Strike or HitIntoPlay
    action = json_file['summary_acts']['pitch']['action']
        # Foul or FoulTip
    out = json_file['summary_score']['outs']['play']
        # 0 = not out, # 1 = out
    starting_strikes = json_file['summary_score']['count']['strikes']['plateAppearance']
    if result == 'Strike' and not action:
        swing = 'Swing and Miss'
    elif result == 'HitIntoPlay':
        if out == 1:
            swing = 'Hit and Out'
        else:
            swing = 'Hit and Safe'
    elif action == 'Foul':
        swing = 'Hit Foul'
    elif action == 'FoulTip':
        swing = 'Foul Tip'
    else:
        swing = 'Other'
    return swing, starting_strikes


def find_radial_dist(df):
    pairs = combinations(df[['pitch_x', 'pitch_z']].values, 2)

    # Initialize variables to store the maximum distance and corresponding points
    max_distance = 0
    max_pair = None

    # Calculate distances and find the maximum
    for p1, p2 in pairs:
        dist = math.dist(p1, p2)
        if dist > max_distance:
            max_distance = dist
            max_pair = (p1, p2)
    
    return max_pair, max_distance

def score_distances(quality_distances, hunt_distance):
    if hunt_distance < quality_distances[0]:
        score = 4
    elif hunt_distance < quality_distances[1]:
        score = 3
    elif hunt_distance < quality_distances[2]:
        score = 2
    elif hunt_distance < quality_distances[3]:
        score = 1
    else:
        score = 0
    return score

def swing_map_scorecard(hunt_dist, swing_map_df):
    scorecard_list = []
    for batter_id in swing_map_df['batter'].unique():
        scorecard_dict = {'batter': batter_id}
        batter_df = swing_map_df[
            (swing_map_df['batter'] == batter_id)
            &
            (swing_map_df['two_strikes'] == False)
        ].copy()
        if len(batter_df) <= 1:
            continue
        
        # add radius
        max_pair, max_dist = find_radial_dist(batter_df)
        median, distances = geometric_median(batter_df)
        distance_scores = [score_distances(hunt_dist, dist) for dist in distances]
        avg_score = sum(distance_scores) / len(distance_scores)
        scorecard_dict['max_swing_dist'] = max_dist
        scorecard_dict['max_swing_pair'] = max_pair
        scorecard_dict['geometric_median'] = median
        scorecard_dict['point_distances'] = distances
        scorecard_dict['distance_scores'] = distance_scores
        scorecard_dict['avg_score'] = avg_score

        hunt_distance_avg = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
        grade = get_grade(avg_score, hunt_distance_avg)
        scorecard_dict['hunting_grade'] = grade
        scorecard_list.append(scorecard_dict)
    return pd.DataFrame.from_dict(scorecard_list)

def plot_swing_map(swing_map_df, grade, radii=None):
    
    result_colors = {
        'Hit and Safe': 'green',
        'Hit and Out': 'red',
        'Hit Foul': 'blue',
        'Foul Tip': 'orange',
        'Swing and Miss': 'darkred'
    }

    font1 = {'size':22}
    font2 = {'size':18}
    font3 = {'size':14}

    default_fig_size = (6.4, 4.8)
    size_adjust = 1.5
    larger_fig_size = [fig_size * size_adjust for fig_size in default_fig_size]
    fig, axis = plt.subplots(figsize=larger_fig_size)

    if swing_map_df is not None:
        swing_map_df = swing_map_df.copy()
        swing_map_df.loc[:, 'color'] = swing_map_df['swing_result'].map(result_colors)
        results = swing_map_df['swing_result'].unique()
        batter_id = swing_map_df['batter'].iloc[0]

        axis = sns.scatterplot(
            data=swing_map_df[swing_map_df['two_strikes']], 
            x='pitch_x', y='pitch_z', 
            hue='swing_result',
            palette=result_colors,
            alpha=0.5,
            marker='X',
            s=100,
            legend=False
        )
        axis = sns.scatterplot(
            data=swing_map_df[~swing_map_df['two_strikes']], 
            x='pitch_x', y='pitch_z', 
            hue='swing_result',
            palette=result_colors,
            alpha=0.5,
            marker='s',
            s=100
        )

    # add home plate to plot 
    home_plate_coords = [[-0.71, 0], [-0.85, -0.5], [0, -1], [0.85, -0.5], [0.71, 0]]
    axis.add_patch(patches.Polygon(home_plate_coords,
                                edgecolor = 'darkgray',
                                facecolor = 'lightgray',
                                zorder = 0.1))
    
    # add strike zone to plot, technically the y coords can vary by batter
    axis.add_patch(patches.Rectangle((-0.71, 1.5), 2*0.71, 2,
                edgecolor = 'lightgray',
                fill=False,
                lw=3,
                zorder = 0.1))
    
    axis.set_xlim([-3, 3])
    axis.set_ylim([-1.5, 5])

    if radii: 
        # Add expanding circles (hunting radii)
        center=(-0.25, 2.75)
        colors = ['green', 'blue', 'orange', 'red']
        legend_patches = []
        grades = ['Grade A', 'Grade B', 'Grade C', 'Grade D']
        for i, radius in enumerate(radii):
            color = colors[i % len(colors)]  # Cycle through colors if there are more circles than colors
            if i == 0:
                inner_radius = 0
            else:
                inner_radius = radii[i - 1]
            wedge = patches.Wedge(center, radius, 0, 360, width=radius-inner_radius, 
                                  edgecolor=color, facecolor=color, alpha=0.2, zorder=0.1)
            
            axis.add_patch(wedge)
            legend_patches.append(wedge)

        # Add hunting legend
        hunting_legend = axis.legend(legend_patches, grades, loc='upper right',
                                    fontsize=font3['size'],
                                    title='Hunting Radii', title_fontsize=font2['size'])

    if swing_map_df is not None: 
        axis.text(-2.8, -1, grade, fontsize=100, color=color_letter(grade))

        # # Produce a legend with custom markers
        handles, labels = axis.get_legend_handles_labels()
        legend_elements = [
            Line2D([0], [0], marker='X', color='w', label='Two-strike pitches', 
                markerfacecolor='grey', markersize=10),
            Line2D([0], [0], marker='s', color='w', label='Other pitches', 
                markerfacecolor='grey', markersize=10)
        ]
        legend_handles = [Line2D([], [], color=h, linestyle='', alpha=0.5,
                    marker='o', label=l) 
            for l, h in result_colors.items() if l in results]
        legend_elements.extend(legend_handles)
        axis.legend(handles=legend_elements, loc="best", title=None, prop=font3)

        subtitle = f'\n Batter: {batter_id}'
    else:
        subtitle = ""


    plt.title(f'Hunting Pitches{subtitle}', font1)
    plt.grid(False)
    plt.axis('off')
    plt.xlabel(None)
    plt.ylabel(None)
    
    return fig

if __name__ == '__main__':

    hunting_defaults = [0.5, 0.75, 1, 1.25]
    swing_map_df = pd.read_csv('../data/dataframes/swing_map_metrics_df.csv')
    scorecard_df = swing_map_scorecard(hunting_defaults, swing_map_df)

    # batter_list = swing_map_df.batter.unique()
    batter_list = [459722179, 558675411, 545569723]
        # need to add code to save the resulting plots
    for batter_id in batter_list:
        batter_df = swing_map_df[
            (swing_map_df['batter'] == batter_id)
            # two strike swings are being included here for plotting, 
            # but dropped when calculating max distance
        ]
        if len(batter_df) == 1:
            continue
        grade = scorecard_df[scorecard_df['batter'] == batter_id]['hunting_grade'].values[0]
        plot_swing_map(batter_df, grade)
        plt.show()
        # plt.savefig(f'../images/grades/{batter_id}_hunting.png')

    plot_swing_map(None, None, hunting_defaults)
    plt.show()