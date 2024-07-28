import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_grade(distance, thresholds):
    """
    Assign a grade based on the distance value and predefined thresholds.

    Args:
        distance (float): The distance value.
        thresholds (dict): The grade thresholds.

    Returns:
        str: The assigned grade.
    """
    # should this be moved to a utils file?
    if distance >= thresholds["A"]:
        return "A"
    elif distance >= thresholds["B"]:
        return "B"
    elif distance >= thresholds["C"]:
        return "C"
    elif distance >= thresholds["D"]:
        return "D"
    else:
        return "F"


def color_letter(grade):
    """
    Get the color associated with a grade.

    Args:
        grade (str): The grade.

    Returns:
        str: The color associated with the grade.
    """
    # should this be moved to a utils file?
    color_dict = {"A": "green", "B": "blue", "C": "orange", "D": "red", "F": "red"}
    return color_dict[grade]

