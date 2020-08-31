import json


def read_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data


def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)
