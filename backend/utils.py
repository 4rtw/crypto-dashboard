import json
import os
import numpy as np
import pandas as pd
from typing import Any, Union, Dict, List

def load_json(path: str) -> Union[Dict, List]:
    """
    Safely loads JSON data from a file.

    Args:
        path (str): The path to the JSON file.

    Returns:
        Union[Dict, List]: The loaded data, or an empty list/dict if the file doesn't exist or is invalid.
    """
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return [] if "history" in path else ({} if "config" in path else [])
    return [] if "history" in path else ({} if "config" in path else [])

def save_json(path: str, data: Any) -> None:
    """
    Saves data to a JSON file.

    Args:
        path (str): The path to the JSON file.
        data (Any): The data to save.
    """
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except IOError:
        pass  # In a real app, you might want to log this error.

def json_safe(data: Any) -> Any:
    """
    Recursively sanitizes data to be JSON serializable, handling NaN and Infinity.

    Args:
        data (Any): The data to sanitize.

    Returns:
        Any: The sanitized data.
    """
    if isinstance(data, dict):
        return {k: json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [json_safe(v) for v in data]
    elif isinstance(data, (float, np.float32, np.float64)):
        if np.isnan(data) or np.isinf(data):
            return 0.0
        return float(round(data, 4))
    return data

def sanitize_float(val: Any) -> float:
    """
    Safely converts a value to a float, handling NaN and Infinity.

    Args:
        val (Any): The value to convert.

    Returns:
        float: The converted float, or 0.0 if conversion fails or the value is invalid.
    """
    try:
        f = float(val)
        if pd.isna(f) or np.isinf(f):
            return 0.0
        return f
    except (ValueError, TypeError):
        return 0.0
