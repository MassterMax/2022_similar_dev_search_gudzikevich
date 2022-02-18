import json
from typing import Dict, List, Union


def save_data_as_json(data: Union[List, Dict], path: str):
    """
    A method to serialize json-like object
    Args:
        data: data to save
        path: path to save like C:/path/to/file.json

    Returns:

    """
    with open(path, "w+") as fp:
        json.dump(data, fp)
