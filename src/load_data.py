import json

def load_profiles(path):

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return data["data"]