import json
import os

def load_config():
    """
    Loads configuration from 'config.json' or 'config.example.json'.
    """
    config_path = 'config.json'
    if not os.path.exists(config_path):
        config_path = 'config.example.json'

    with open(config_path, 'r') as f:
        return json.load(f)
