import json
import os

def load_config(path: str = "config.json") -> dict:
    """
    Loads configuration from the specified path.
    Falls back to `config.example.json` if the primary path is not found.
    """
    if not os.path.exists(path):
        alt_path = os.path.join(os.path.dirname(__file__) or ".", "config.example.json")
        if not os.path.exists(alt_path):
            raise FileNotFoundError("缺少配置文件，请创建 config.json 或保留 config.example.json")
        path = alt_path

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
