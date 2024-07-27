import math
import pandas as pd
from distance import get_grade, color_letter

import plotly.graph_objects as go
from PIL import Image
import requests
from io import BytesIO

def find_sweet_spot(head_pos, handle_pos):
    return head_pos - 0.175 * (head_pos - handle_pos)

def calc_attack_angle(yz_path, bat_loc, hit_frame):
    cols = ['time', f'{bat_loc}_pos_1', f'{bat_loc}_pos_2']
    hit_row = hit_frame[cols]
    trough_row = yz_path.loc[yz_path[f'{bat_loc}_pos_2'].idxmin(), cols]
    angle_df = hit_row - trough_row
    y = angle_df[f'{bat_loc}_pos_1'].iloc[0]
    z = angle_df[f'{bat_loc}_pos_2'].iloc[0]
    return math.degrees(math.atan(z/y))

def get_ball_contact_idx(ball_df, contact_time):
    ball_df['contact_time_diff'] = abs(ball_df['time'] - contact_time)
    return ball_df['contact_time_diff'].idxmin() 

def calc_pitch_angle(ball_df, contact_time):
    ball_df_dedup = ball_df.drop_duplicates().reset_index()
    cols = ['time', 'pos_0', 'pos_1', 'pos_2']
    contact_idx = get_ball_contact_idx(ball_df_dedup, contact_time)
    contact_row = ball_df_dedup.loc[contact_idx, :]
    pre_contact_row = ball_df_dedup.loc[contact_idx-1, cols]
    ball_angle_df = contact_row - pre_contact_row
    y = ball_angle_df['pos_1']
    z = ball_angle_df['pos_2']
    return math.degrees(math.atan(z/y))

def find_track_angle(ball_df, bat_df, hit_frame):
    '''
    Track angle is the difference between the attack angle and the pitch angle. 
    It provides a measure of how well the batter is tracking and attacking the pitch.
    '''
    hit_df = hit_frame.copy()
    for ax in ['1', '2']:
        bat_df[f'sweet_spot_pos_{ax}'] = bat_df.apply(
            lambda x:find_sweet_spot(x[f'head_pos_{ax}'], x[f'handle_pos_{ax}']), axis=1
        )
        hit_df[f'sweet_spot_pos_{ax}'] = hit_df.apply(
            lambda x:find_sweet_spot(x[f'head_pos_{ax}'], x[f'handle_pos_{ax}']), axis=1
        )
    attack_angle = calc_attack_angle(bat_df, 'sweet_spot', hit_df)
    contact_time = hit_frame['time'].values[0]
    pitch_angle = calc_pitch_angle(ball_df, contact_time)
    return attack_angle, (attack_angle - pitch_angle)

def group_angles(x, angle_ranges):
    group=0
    for i, angle in enumerate(angle_ranges):
        if x > angle[0]:
            group=i
            continue
    return group

def get_group_frequencies(df, group):
    freq = len(df[df['angle_group'] == group])/len(df)
    return (group, freq)

def convert_angle_freqs_to_score(angle_freqs):
    middle = math.floor(len(angle_freqs)/2)
    mid_angle_freqs = [(abs(i-middle), j) for i, j in angle_freqs]
    mid_angle_freqs_dict = dict()
    for i, freq in mid_angle_freqs:
        if i in mid_angle_freqs_dict.keys():
            mid_angle_freqs_dict[i] += freq
        else:
            mid_angle_freqs_dict[i] = freq
    freq_max = max(mid_angle_freqs_dict.values())
    max_keys = [k for k, v in mid_angle_freqs_dict.items() if v == freq_max]
    dict_len = len(mid_angle_freqs_dict)
    score = dict_len - max(max_keys)
    thresholds = {'A':dict_len, 'B':dict_len-1, 'C':dict_len-2, 'D':dict_len-3}
    return get_grade(score, thresholds)

def score_timing_angle(score_ranges, angle):
    angle = abs(angle)
    half_range = math.floor(len(score_ranges)/2)
    quality_ranges = score_ranges[half_range:]
    if 0 <=  angle < quality_ranges[0][1]:
        score = 4
    elif quality_ranges[1][0] <= angle < quality_ranges[1][1]:
        score = 3
    elif quality_ranges[2][0] <= angle < quality_ranges[2][1]:
        score = 3
    elif quality_ranges[3][0] <= angle < quality_ranges[3][1]:
        score = 2
    elif quality_ranges[4][0] <= angle < quality_ranges[4][1]:
        score = 1
    else:
        score = 0
    return score

def tracking_scorecard(tracking_df, angle_ranges):
    scorecard_list = []
    for batter in tracking_df['batter'].unique():
        scorecard_dict = dict()
        scorecard_dict['batter'] = batter

        batter_df = tracking_df[
            (tracking_df['batter'] == batter)
            &
            (tracking_df['track_angle'].notnull())
        ].copy()

        if len(batter_df) == 0:
            continue
        batter_df['angle_group'] = batter_df.apply(
            lambda x: group_angles(x['track_angle'], angle_ranges),
            axis=1
        )

        angle_freqs = [get_group_frequencies(batter_df, g) for g in range(len(angle_ranges))]
        angle_scores = [score_timing_angle(angle_ranges, angle) for angle in batter_df['track_angle']]
        scorecard_dict['angle_freqs'] = angle_freqs
        scorecard_dict['angle_scores'] = angle_scores
        old_grade = convert_angle_freqs_to_score(angle_freqs)
        batter_score = sum(angle_scores) / len(angle_scores)
        thresholds = {'A': 3.25, 'B': 3, 'C': 2.5, 'D': 2}
        scorecard_dict['track_angle_grade'] = get_grade(batter_score, thresholds)
        scorecard_list.append(scorecard_dict)
    return scorecard_list

def convert_score_ranges(score_ranges):
    ranges = []
    for i, score in enumerate(score_ranges):
        if i == 0:
            ranges.append((-score, score))
        else:
            ranges.append((ranges[i-1][1], ranges[i-1][1]+score))
    neg_ranges = [(-end, -start) for start, end in ranges[1:]]

    #assumes the outer edge is less than 90 degrees from pitch angle
    lower_edge = [(-90,neg_ranges[-1][0])]
    upper_edge = [(ranges[-1][1],90)]
    ranges.extend(neg_ranges)
    ranges.extend(lower_edge)
    ranges.extend(upper_edge)
    ranges.sort(key=lambda tup: tup[0])
    centers = [sum(edges)/len(edges) for edges in ranges]
    widths = [end-start for start, end in ranges]
    return ranges, centers, widths

def polar_to_cartesian(r, theta_deg):
    # polar coordinates start at approximately (1.5, 1.95)
    theta_rad = math.radians(theta_deg + 2)
    x = -r * math.cos(theta_rad) + 1.5
    y = r * math.sin(theta_rad) + 1.95
    return x, y


def plot_tracking_angles(score_ranges, alphas=None, grade=None, 
                           color=None, batter_id=None):
    pitch_angle = 10
    _, centers, widths = convert_score_ranges(score_ranges)
    theta_list = [-theta - pitch_angle for theta in centers]

    marker_colors = ['darkslateblue'] * len(widths)
    marker_colors[4:6] = ['magenta']*2

    if batter_id is not None:
        colors = [f'rgba(0,136,255,{a})' for a in alphas]
        sorted_colors = list(set(colors.copy()))
        sorted_colors.sort(reverse=True)
        names = [""] * len(sorted_colors)
        names[0] = "High"
        names[-1] = "Low"
    else:
        base_colors = ['#FF0000', '#FFA500', '#0000FF', '#008000', '#0000FF', '#FFA500', '#FF0000']
        alpha_value = 0.3  # Adjust this to control transparency
        colors = [f'rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},{alpha_value})' 
                  for color in base_colors]
        colors.append('white')
        colors.insert(0, 'white')
        sorted_colors = colors[4:8]
        names = ['Grade A', 'Grade B', 'Grade C', 'Grade D']



    data = [
        go.Barpolar(
            r=[5]*len(widths),
            theta=theta_list,
            width=widths,
            marker_color=colors,
            marker_line_color=marker_colors,
            marker_line_width=2,
            legend="legend"
        )
    ]

    legends = [
        go.Barpolar(
            r=[None],
            theta=[None],
            marker_color=sorted_colors[i],
            marker_line_color='darkslateblue',
            marker_line_width=2,
            name=names[i],
            legend="legend2"
        ) for i in range(len(sorted_colors))
    ]
    data.extend(legends)
    fig = go.Figure(data,
    layout={"legend":{'visible': False},
            "legend2": {'font': {"size": 20},
                         'title': 'Swing Frequency',
                         'xref': 'paper',
                         'x': 0.75,
                         'itemsizing': 'constant'
                         }
            }
    )
    
    fig.add_annotation(text="Tracking Angle", font={'size':30},
                       xref="paper", yref="paper",
                       x=0.5, y=1.25, showarrow=False)
    
    if batter_id is not None: 
        fig.add_annotation(text=grade, font={'size':100, 'color':color},
                        xref="paper", yref="paper",
                        x=0.25, y=0, showarrow=False)


        fig.add_annotation(text=f"Batter: {batter_id}", font={'size':30},
                        xref="paper", yref="paper",
                        x=0.5, y=1.15, showarrow=False)
        
        for i in range(8):
            # Set the polar coordinates for the image
            r_image = (i)*0.3 
            theta_image = pitch_angle + 4  

            # Convert polar to Cartesian for image placement
            x_image, y_image = polar_to_cartesian(r_image, theta_image)
            url = "https://raw.githubusercontent.com/woodmc10/wisd_2024/main/images/pieces/baseball_1.png"
            # Fetch the image from the URL
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            # add image to plot
            fig.add_layout_image(
                dict(
                    source=img,
                    xref="x",
                    yref="y",
                    xanchor="center",
                    yanchor="middle",
                    x=x_image,
                    y=y_image,
                    sizex=0.18,
                    sizey=0.18,
                    sizing="contain",
                    opacity=1,
                    layer="above"
                )
            )
    
    
    fig.update_layout(
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False
        ),
        template=None,
        polar=dict(
            radialaxis=dict(range=[0, 5], showticklabels=False, ticks=''),
            angularaxis=dict(showticklabels=False, ticks=''),
            # sector=[-pitch_angle - 90, -pitch_angle + 90]
            sector=[-pitch_angle - 45, -pitch_angle + 45]
        )
    )

    if batter_id is not None: 
        fig.update_layout(
            autosize=True,
            width=1200,
            height=600
        )
    else:
        fig.update_layout(
            width=700,
            height=500
        )
    
    fig.update_layout(showlegend=True)

    return fig

def generate_track_angle_plot(batter_id, tracking_score_df, score_widths):
    batter_df = tracking_score_df[tracking_score_df['batter'] == batter_id]
    percents = [group_freq[1] for group_freq in batter_df['angle_freqs'].values[0]]
    alphas = [per/max(percents) for per in percents]
    grade = batter_df['track_angle_grade'].values[0]
    color = color_letter(grade)
    return plot_tracking_angles(score_widths, alphas, grade, color, batter_id)

def create_tracking_score_df(score_widths, tracking_metrics_df):
    score_ranges, _, _ = convert_score_ranges(score_widths)
    tracking_score_list = tracking_scorecard(tracking_metrics_df, score_ranges)
    return pd.DataFrame.from_dict(tracking_score_list)

if __name__ == '__main__':
# Needs to be updated, copied from timing
    tracking_metrics_df = pd.read_csv('../data/dataframes/tracking_metrics_df.csv')

    score_widths = [2.5, 5, 10, 15]
    tracking_score_df = create_tracking_score_df(score_widths, tracking_metrics_df)

    batter_list = [545569723, 590082479]
        # when ready, create a list of all batters in scorecard_df and loop through
            # need to add code to save the resulting plots
    for batter_id in batter_list:
        fig = generate_track_angle_plot(batter_id, tracking_score_df, score_widths)
        fig.show()
        # fig.write_image(f'../images/grades/{batter_id}_tracking.png')
    fig = plot_tracking_angles(score_widths)
    fig.show()
