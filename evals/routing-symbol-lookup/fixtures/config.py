import json


def parse_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def reload(path):
    return parse_config(path)
