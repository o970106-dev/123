# -*- coding: utf-8 -*-
import json
import os

def load_config(path: str = "config.json") -> dict:
    """
    從指定的路徑載入 JSON 設定檔。

    如果 `config.json` 不存在，會嘗試退回使用 `config.example.json`。
    """
    if not os.path.exists(path):
        example_path = "config.example.json"
        if not os.path.exists(example_path):
            raise FileNotFoundError(
                "找不到 config.json 或 config.example.json"
            )

        print(f"[提示] 找不到 {path}，將使用 {example_path} 作為設定")
        path = example_path

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
