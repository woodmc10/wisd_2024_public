import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def filter_path(path_df):
    mid_index = path_df.index[path_df.event.isin(['Hit', 'Nearest'])].to_list()
    start_index = mid_index[0] - 50
    end_index = mid_index[0] + 50
    return path_df[start_index:end_index]

def normalize_path(path):
    if path['handle_pos_0'].iloc[0] < 0:
        path['head_pos_0'] = path['head_pos_0'] * -1
        path['handle_pos_0'] = path['handle_pos_0'] * -1
    pos_columns = ['head_pos_0', 'head_pos_1', 'head_pos_2',
                   'handle_pos_0', 'handle_pos_1', 'handle_pos_2']
    return path[pos_columns] - path[pos_columns].iloc[0]

def combine_coordinates(df):
    return df[['head_pos_0', 'head_pos_1', 'head_pos_2',
               'handle_pos_0', 'handle_pos_1', 'handle_pos_2'
              ]].values


def get_grade(distance, thresholds):
    # should this be moved to a utils file?
    if distance >= thresholds['A']:
        return 'A'
    elif distance >= thresholds['B']:
        return 'B'
    elif distance >= thresholds['C']:
        return 'C'
    elif distance >= thresholds['D']:
        return 'D'
    else:
        return 'F'
    
def convert_column_name(column_name):
    # should this be moved to a utils file?
    bat_section = column_name.split('_')[0].capitalize()
    axes_list = ['X', 'Y', 'Z']
    letter = axes_list[int(column_name.split('_')[-1])]
    return f'{bat_section} {letter}'

def color_letter(grade):
    # should this be moved to a utils file?
    color_dict = {
        'A': 'green',
        'B': 'blue',
        'C': 'orange',
        'D': 'red',
        'F': 'red'
    }
    return color_dict[grade]

def distance_scorecard(dist_grades, distance_df): 
    batters = distance_df.batter.unique()
    scorecard_list = []
    for batter in batters:
        scorecard_dict = dict()
        scorecard_dict['batter'] = batter
        scorecard_dict['reference_file'] = distance_df[(distance_df['batter'] == batter) & (distance_df['distance'] == 0.0)]['file'].values[0]
        batter_df = distance_df[(distance_df['batter'] == batter) & (distance_df['distance'] > 0)]
            # distance values of -2, -1, and 0 indicate specific data situations, and should not
            # be included in the variance calculations
        if len(batter_df) == 0:
            continue
        min_dist = np.mean(batter_df['distance']) - 2 * np.std(batter_df['distance'])
        max_dist = np.mean(batter_df['distance']) + 2 * np.std(batter_df['distance'])
        swing_count = len(batter_df)
        good_count = len(batter_df[
                        (batter_df['distance'] < max_dist)
                        &
                        (batter_df['distance'] > min_dist)
                        ])
        scorecard_dict['dist_score'] = good_count/swing_count
        distance_thresholds = {
            'A': dist_grades[0],
            'B': dist_grades[1],
            'C': dist_grades[2],
            'D': dist_grades[3]
        }
        scorecard_dict['dist_grade'] = get_grade(good_count/swing_count, distance_thresholds)
        scorecard_dict['compare_file'] = batter_df[batter_df['distance'] == max(batter_df['distance'])]['file'].values[0]
        scorecard_list.append(scorecard_dict)
    return pd.DataFrame.from_dict(scorecard_list)

if __name__ == '__main__':

    distance_metrics_df = pd.read_csv('../data/dataframes/distance_metrics_df.csv')

    dist_defaults = [1.0, 0.95, 0.9, 0.85]
    scorecard_df = distance_scorecard(dist_defaults, distance_metrics_df)
    batter_list = [223971350]