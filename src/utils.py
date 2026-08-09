import json
from pathlib import Path


def read_json(path: str) -> dict:
    """
    Read a json file
    :param path: path to json file
    :return: JSON data
    """
    with open(path, 'r') as f:
        return json.load(f)


def get_project_root() -> Path:
    """Traverses up until it finds a root marker file."""
    for parent in Path(__file__).resolve().parents:
        if (parent / '.git').exists() or (parent / 'pyproject.toml').exists():
            return parent
    return Path(__file__).resolve().parent # Fallback to current script folder
