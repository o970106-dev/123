import json
import os


def load_config():
    if not os.path.exists("config.json"):
        alt = "config.example.json"
        if not os.path.exists(alt):
            raise FileNotFoundError("Missing config.json or config.example.json")
        print(f"[info] using example config: {alt}")
        path = alt
    else:
        path = "config.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
