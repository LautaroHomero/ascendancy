import json
from pathlib import Path


def load_profiles(path: str) -> list:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in '{path}': {e}") from e

    if not isinstance(data, dict):
        raise TypeError(
            "Invalid JSON format: expected the root element to be an object."
        )

    if "data" not in data:
        raise KeyError("Missing required field: 'data'.")

    profiles = data["data"]

    if profiles is None:
        raise ValueError("Field 'data' cannot be null.")

    if not isinstance(profiles, list):
        raise TypeError(
            f"Field 'data' must be a list, got {type(profiles).__name__}."
        )

    if len(profiles) == 0:
        raise ValueError("Field 'data' is empty.")

    return profiles