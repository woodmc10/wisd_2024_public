import streamlit as st
import pandas as pd
import plotly.io as pio
from PIL import Image
from io import BytesIO
from track_angle import (
    plot_tracking_angles,
    create_tracking_score_df,
    generate_track_angle_plot,
)
from hunt import plot_hunting
from contact_loc import viz_contact_loc
from scorecard import generate_scorecard

# Load data
github = "https://raw.githubusercontent.com/woodmc10/wisd_2024_public/main"
# github = ".."
data_folder = f"{github}/data/dataframes"
image_folder = f"{github}/images/grades"

swing_map_df = pd.read_csv(f"{data_folder}/swing_map_metrics_df.csv")
tracking_metrics_df = pd.read_csv(f"{data_folder}/tracking_metrics_df.csv")
timing_metrics_df = pd.read_csv(f"{data_folder}/timing_metrics_df.csv")
similarity_metrics_df = pd.read_csv(f"{data_folder}/distance_metrics_df.csv")

# Define metric options
metric_options = [
    ("Contact Location"),
    ("Tracking Angle"),
    ("Hunting Pitches"),
    ("Swing Similarity"),
]

# Define grade values for widgets
widget_grades = ["Grade A", "Grade B", "Grade C", "Grade D"]


def save_widget_states():
    """
    Saves the current state of all Streamlit widgets to the session state.
    """
    for key in st.session_state.keys():
        key_default = f"{key}_default"
        if key_default in st.session_state:
            st.session_state[key_default] = st.session_state[key]


def get_slider_values():
    """
    Retrieves the current values of all sliders and dropdowns from the session state.

    Returns:
        dict: A dictionary containing current slider values and metric order.
    """
    return {
        "contact_locations": [
            st.session_state.get(f"contact_location_{i}_default", (0.5, 1)) for i in range(4)
        ],
        "hunting_dists": [
            st.session_state.get(f"hunting_{i}_default", (1.0, 2.0)) for i in range(4)
        ],
        "track_angles": [
            st.session_state.get(f"track_angle_{i}_default", 5) for i in range(4)
        ],
        "swing_similarities":[
            st.session_state.get(f'swing_similarity_{i}_default', (0.9, 1.0)) for i in range(4)
        ],
        "metric_order": [
            st.session_state.get(f"priority_{i}_default", "Contact Location")
            for i in range(4)
        ],
    }

def update_sliders(slider_idx, metric, direction="increasing"):
    """
    Update the values of sliders above and below the currently adjusted slider to maintain linked ranges.

    Args:
    slider_idx (int): The index of the currently adjusted slider.
    metric (str): The metric associated with the sliders (e.g., 'contact_location').
    direction (str, optional): The direction in which the values should be propagated. 
                               Defaults to "increasing". Can be "increasing" or "decreasing".

    This function dynamically updates the default values of sliders based on the selected value of the current slider. 
    If `direction` is "increasing", it updates the slider below to start where the current slider ends. 
    If `direction` is "decreasing", it updates the slider above to end where the current slider starts.
    """
    value = st.session_state[f"{metric}_{slider_idx}"]
    st.session_state[f"{metric}_{slider_idx}_default"] = value
    current_bottom = value[0]
    current_top = value[1]

    # Update slider below the current one 
    if slider_idx < 3:
        below = st.session_state[f"{metric}_{slider_idx+1}_default"]
        below_top = below[1]
        below_bottom = below[0]
        if direction == "increasing":
            st.session_state[f"{metric}_{slider_idx+1}_default"] = (current_top, below_top)
        elif direction == "decreasing":
            st.session_state[f"{metric}_{slider_idx+1}_default"] = (below_bottom, current_bottom)
    
    # Update sliders above the current one
    if slider_idx > 0:
        above = st.session_state[f"{metric}_{slider_idx-1}_default"]
        above_bottom = above[0]
        above_top = above[1]
        if direction == "increasing":
            st.session_state[f"{metric}_{slider_idx-1}_default"] = (above_bottom, current_bottom)
        if direction == "decreasing":
            st.session_state[f"{metric}_{slider_idx-1}_default"] = (current_top, above_top)


def display_scorecard():
    """
    Generates and displays the scorecard based on the current slider values and priorities.

    Returns:
        pd.DataFrame: The generated scorecard DataFrame.
    """
    # save the widget states to use metric priorities and swing count widget values
    save_widget_states()
    # collect widget values
    values = get_slider_values()
    min_swing_count = st.session_state["swing_count_default"]
    
    contact_locs = [locs[1] for locs in values["contact_locations"]]
    top = [values["contact_locations"][-1][0]]
    contact_locs.extend(top)
    # build scorecard with custom criteria
    df = generate_scorecard(
        data_folder,
        contact_locs,
        values["track_angles"],
        [loc[1] for loc in values["hunting_dists"]],
        [loc[1] for loc in values['swing_similarities']],
    )
    # prep dataframe to show custom sort order and readable columns
    df_min_swings = df[df["swing_count"] >= min_swing_count]
    scorecard = df_min_swings[
        ["batter", "swing_count", "timing_grade", "track_angle_grade", "hunting_grade", "dist_grade"]
    ]
    column_name_map = {
        "batter": "Batter ID",
        "swing_count": "Swing Count",
        "timing_grade": "Contact Location",
        "track_angle_grade": "Tracking Angle",
        "hunting_grade": "Hunting Pitches",
        "dist_grade": "Swing Similarity",
    }

    display_scorecard = scorecard.copy()
    display_scorecard.rename(columns=column_name_map, inplace=True)
    display_scorecard = display_scorecard.sort_values(values["metric_order"])
    # store the batter list for use in dropdown
    st.session_state["batter_list"] = display_scorecard["Batter ID"].tolist()
    # change batter id to string to make prettier
    display_scorecard["Batter ID"] = (
        display_scorecard["Batter ID"].astype(int).astype(str)
    )
    # sort display columns to match priority order
    priority_metrics = pd.Series(values["metric_order"]).drop_duplicates().tolist()
    all_metrics = [option for option in metric_options]
    display_columns = ["Batter ID", "Swing Count"]
    missing_metrics = set(all_metrics).difference(set(priority_metrics))
    display_columns.extend(list(priority_metrics))
    display_columns.extend(list(missing_metrics))
    display_scorecard = display_scorecard[display_columns]

    st.write(display_scorecard)
    return scorecard


def extract_image(fig):
    """
    Converts a Plotly figure to a PIL Image.

    Args:
        fig (plotly.graph_objs._figure.Figure): The Plotly figure to convert.

    Returns:
        PIL.Image.Image: The converted image.
    """
    img_bytes = pio.to_image(fig, format="png", scale=2)
    img = Image.open(BytesIO(img_bytes))
    return img


def filter_middle_percent(image, percentage=50):
    """
    Crops the image to the middle percentage of its width.

    Args:
        image (PIL.Image.Image): The image to crop.
        percentage (int, optional): The percentage of the width to keep. Defaults to 50.

    Returns:
        PIL.Image.Image: The cropped image.
    """
    width, height = image.size
    left = int((100 - percentage) / 2 * width / 100)
    right = width
    top = 0
    bottom = height

    # Crop the image to the middle 50%
    cropped_img = image.crop((left, top, right, bottom))
    return cropped_img

def tracking_plot(batter_id):
    """
    Displays tracking angle plot for the selected batter.

    Args:
        batter_id (int): The ID of the selected batter.
    """
    st.subheader("Tracking Angle Plot")
    try:
        tracking_df = create_tracking_score_df(
            get_slider_values()["track_angles"], tracking_metrics_df
        )
        track_fig = generate_track_angle_plot(
            batter_id, tracking_df, get_slider_values()["track_angles"]
        )

        # Extract and display image
        image = extract_image(track_fig)
        st.image(image, use_column_width=True)

    except Exception as e:
        st.error(f"Error in plot_tracking_angles: {e}")

def hunting_plot(batter_id):
    """
    Displays hunting pitches plot for the selected batter.

    Args:
        batter_id (int): The ID of the selected batter.
    """
    st.subheader("Hunting Pitches Plot")
    try:
        hunt_grade = scorecard.query(f"batter == {batter_id}")[
            "hunting_grade"
        ].item()
        batter_map = swing_map_df.query(f"batter == {batter_id}")
        hunt_fig = plot_hunting(batter_map, hunt_grade)
        st.pyplot(hunt_fig)
    except Exception as e:
        st.error(f"Error in plot_hunting: {e}")

    
def contact_loc_plot(batter_id):
    """
    Displays contact location plot for the selected batter.

    Args:
        batter_id (int): The ID of the selected batter.
    """
    st.subheader("Contact Location Plot")
    try:
        loc_grade = scorecard.query(f"batter == {batter_id}")[
            "timing_grade"
        ].item()
        batter_timing = timing_metrics_df.query(f"batter == {batter_id}")

        plot_locs = [locs[1] for locs in get_slider_values()["contact_locations"]]
        top = [get_slider_values()["contact_locations"][-1][0]]
        plot_locs.extend(top)

        loc_fig = viz_contact_loc(
            batter_timing,
            loc_grade,
            plot_locs,
        )
        st.pyplot(loc_fig)
    except Exception as e:
        st.error(f"Error in viz_contact_loc: {e}")

def swing_sim_plot(batter_id):
    """
    Displays swing similarity plot for the selected batter.

    Args:
        batter_id (int): The ID of the selected batter.
    """
    st.subheader("Swing Similarity Plot")
    try:
        sim_plot = f"{image_folder}/{batter_id}_similarity.png"
        st.image(sim_plot)
    except Exception as e:
        st.error(f"Error in similarity plot: {e}")

def update_plots(batter_id):
    """
    Displays the plots based on the selected batter ID and metric priority order.

    Args:
        batter_id (int): The ID of the selected batter.
    """
    # Get priority order and add any unselected metrics to end
    values = get_slider_values()
    priorities = pd.Series(values["metric_order"]).drop_duplicates().tolist()
    unset_priorities = [order for order in metric_options if order not in priorities]
    priorities.extend(unset_priorities)

    for metric in priorities: 
        st.markdown("<br>", unsafe_allow_html=True)
        if metric == "Contact Location":
            contact_loc_plot(batter_id)
        elif metric == "Tracking Angle":
            tracking_plot(batter_id)
        elif metric == "Hunting Pitches":
            hunting_plot(batter_id)
        elif metric == "Swing Similarity":
            swing_sim_plot(batter_id)
        else:
            st.write("An unexpected plotting option was provided")
            
# -------------------------------------------------------
# Initialize session state for sliders and dropdowns if not already set
contact_locs_defaults = [(0.75, 1.5), (0.25, 0.75), (-0.5, 0.25), (-1.5, -0.5)]
if "initialized" not in st.session_state:
    for i in range(4):
        st.session_state[f"contact_location_{i}_default"] = contact_locs_defaults[i]
        st.session_state[f"hunting_{i}_default"] = (0.5 + 0.2 * i, 0.5 + 0.2 * (i + 1))
        st.session_state[f"track_angle_{i}_default"] = 5
        st.session_state[f"swing_similarity_{i}_default"] = (1 - 0.1 * (i + 1), 1 - 0.1 * i)
        st.session_state[f"priority_{i}_default"] = metric_options[i]
    st.session_state["swing_count_default"] = 2
    st.session_state["initialized"] = True

# Main title
st.title("Baseball Swing Scouting Dashboard")

# Tabs for UI
tab_selection = st.sidebar.radio(
    "Select Tab",
    ["Customize Grading", "Scorecard", "Batter Plots"],
    on_change=save_widget_states,
)

if tab_selection == "Customize Grading":
    st.header("Customize Grading for Swing Metrics")

    st.subheader("Contact Location")
    col1, col2 = st.columns([1, 3])

    with col1:
        contact_location = [
            st.slider(
                widget_grades[i],
                -1.5,
                2.0,
                st.session_state[f"contact_location_{i}_default"],
                step=0.25,
                key=f"contact_location_{i}",
                on_change=update_sliders,
                args=(i, "contact_location", "decreasing"),
            )
            for i in range(4)
        ]

    with col2:
        plot_locs = [locs[1] for locs in contact_location]
        top = [contact_location[-1][0]]
        plot_locs.extend(top)
        try:
            fig_location = viz_contact_loc(None, None, plot_locs)
            st.pyplot(fig_location)
        except Exception as e:
            st.write(plot_locs)
            st.error(f"Error in viz_contact_loc: {e}")

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Pitch Hunting")
    col1, col2 = st.columns([1, 3])

    with col1:
        hunting = [
            st.slider(
                widget_grades[i],
                0.0,
                2.0,
                st.session_state[f"hunting_{i}_default"],
                step=0.1,
                key=f"hunting_{i}",
                on_change=update_sliders,
                args=(i, "hunting", "increasing"),
            )
            for i in range(4)
        ]

    with col2:
        try:
            tops = [locs[1] for locs in hunting]
            fig_swing = plot_hunting(None, None, tops)
            st.pyplot(fig_swing)
        except Exception as e:
            st.error(f"Error in plot_hunting: {e}")

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Tracking Angle")
    col1, col2 = st.columns([1, 3])

    with col1:
        track_angle = [
            st.selectbox(
                widget_grades[i],
                [2.5, 5, 10, 15],
                [2.5, 5, 10, 15].index(st.session_state[f"track_angle_{i}_default"]),
                key=f"track_angle_{i}",
            )
            for i in range(4)
        ]

    with col2:
        try:
            fig_tracking = plot_tracking_angles(track_angle)

            # Extract, filter and display image
            image = extract_image(fig_tracking)
            filtered_image = filter_middle_percent(image, percentage=50)
            st.image(filtered_image, use_column_width=True)

        except Exception as e:
            st.error(f"Error in plot_tracking_angles: {e}")

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Swing Similarity
    st.subheader("Swing Similarity")
    col1 = st.columns(1)[0]

    with col1:
        swing_similarity = [st.slider(widget_grades[i], 0.5, 1.0,
                                      st.session_state[f'swing_similarity_{i}_default'],
                                      step=0.05,
                                      key=f"swing_similarity_{i}",
                on_change=update_sliders,
                args=(i, "swing_similarity", "decreasing"),) for i in range(4)]

# ------------------------------------------------
elif tab_selection == "Scorecard":
    st.sidebar.header("Metric Priorities")

    metric_priorities = [
        st.sidebar.selectbox(
            f"Priority {i+1}",
            metric_options,
            metric_options.index(st.session_state[f"priority_{i}_default"]),
            key=f"priority_{i}",
            on_change=save_widget_states,
        )
        for i in range(4)
    ]

    st.sidebar.header("Minimum Swing Count")
    swing_count = st.sidebar.slider(
        "Minimum Swing Count",
        min_value=2,
        max_value=25,
        value=st.session_state["swing_count_default"],
        key="swing_count",
        on_change=save_widget_states,
    )

    st.header("Scorecard")
    scorecard = display_scorecard()
    st.session_state["scorecard"] = scorecard

# ------------------------------------------------
elif tab_selection == "Batter Plots":
    st.header("Batter Plots")

    scorecard = st.session_state.get("scorecard", pd.DataFrame())

    if not scorecard.empty:
        st.sidebar.header("Select Batter")

        batter_list = st.session_state.get("batter_list", scorecard["batter"].tolist())
        batter_id = st.sidebar.selectbox(
            "Select Batter", batter_list, key="batter_selector"
        )

        if batter_id:
            update_plots(batter_id)
        else:
            st.write("Please select a batter to display metric visuals.")
    else:
        st.write("Scorecard has not been created.")
        st.write("Please go to the Scorecard tab first to create the scorecard")
