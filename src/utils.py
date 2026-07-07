import json


def read_json(path: str) -> dict:
    """
    Read a json file
    :param path: path to json file
    :return: JSON data
    """
    with open(path, 'r') as f:
        return json.load(f)
