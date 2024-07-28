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
            st.session_state.get(f"contact_location_{i}_default", 0.5) for i in range(4)
        ],
        "hunting_dists": [
            st.session_state.get(f"hunting_{i}_default", 1.0) for i in range(4)
        ],
        "track_angles": [
            st.session_state.get(f"track_angle_{i}_default", 5) for i in range(4)
        ],
        "swing_similarities":[
            st.session_state.get(f'swing_similarity_{i}_default', 0.9) for i in range(4)
        ],
        "metric_order": [
            st.session_state.get(f"priority_{i}_default", "Contact Location")
            for i in range(4)
        ],
    }


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
    # build scorecard with custom criteria
    df = generate_scorecard(
        data_folder,
        values["contact_locations"],
        values["track_angles"],
        values["hunting_dists"],
        values['swing_similarities'],
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


# -------------------------------------------------------
# Initialize session state for sliders and dropdowns if not already set
if "initialized" not in st.session_state:
    for i in range(4):
        st.session_state[f"contact_location_{i}_default"] = 1.5 - 0.75 * i
        st.session_state[f"hunting_{i}_default"] = 0.5 + 0.25 * i
        st.session_state[f"track_angle_{i}_default"] = 5
        st.session_state[f"swing_similarity_{i}_default"] = 1 - 0.1 * i
        st.session_state[f"priority_{i}_default"] = metric_options[i]
    st.session_state["swing_count_default"] = 2
    st.session_state["initialized"] = True

# Main title
st.title("Baseball Swing Metrics Dashboard")

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
                -1.0,
                2.0,
                st.session_state[f"contact_location_{i}_default"],
                step=0.25,
                key=f"contact_location_{i}",
            )
            for i in range(4)
        ]

    with col2:
        try:
            fig_location = viz_contact_loc(None, None, contact_location)
            st.pyplot(fig_location)
        except Exception as e:
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
                3.0,
                st.session_state[f"hunting_{i}_default"],
                step=0.25,
                key=f"hunting_{i}",
            )
            for i in range(4)
        ]

    with col2:
        try:
            fig_swing = plot_hunting(None, None, hunting)
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
        swing_similarity = [st.slider(widget_grades[i], 0.1, 1.0,
                                      st.session_state[f'swing_similarity_{i}_default'],
                                      step=0.1,
                                      key=f"swing_similarity_{i}",) for i in range(4)]

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

        def update_plots(batter_id):
            """
            Updates the plots based on the selected batter ID.

            Args:
                batter_id (int): The ID of the selected batter.
            """
            if batter_id:
                # Add some spacing
                st.markdown("<br>", unsafe_allow_html=True)
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

                # Add some spacing
                st.markdown("<br>", unsafe_allow_html=True)

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

                # Add some spacing
                st.markdown("<br>", unsafe_allow_html=True)

                st.subheader("Contact Location Plot")
                try:
                    loc_grade = scorecard.query(f"batter == {batter_id}")[
                        "timing_grade"
                    ].item()
                    batter_timing = timing_metrics_df.query(f"batter == {batter_id}")
                    loc_fig = viz_contact_loc(
                        batter_timing,
                        loc_grade,
                        get_slider_values()["contact_locations"],
                    )
                    st.pyplot(loc_fig)
                except Exception as e:
                    st.error(f"Error in viz_contact_loc: {e}")

                # Add some spacing
                st.markdown("<br>", unsafe_allow_html=True)

                st.subheader("Swing Similarity Plot")
                try:
                    sim_plot = f"{image_folder}/{batter_id}_similarity.png"
                    st.image(sim_plot)
                except Exception as e:
                    st.error(f"Error in similarity plot: {e}")

        if batter_id:
            update_plots(batter_id)
    else:
        st.write("Scorecard has not been created.")
        st.write("Please go to the Scorecard tab first to create the scorecard")
