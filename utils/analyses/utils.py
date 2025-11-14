import json


def save_jsonl(filename, data, show: bool = False):
    with open(filename, "a", encoding='utf-8') as file:
        file.write(json.dumps(data) + '\n')
    if show:
        print(json.dumps(data, indent=4))