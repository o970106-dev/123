import json
import os

def load_config(path: str = "config.json") -> dict:
    """
    從指定的路徑載入設定檔。

    如果 `path` 指向的檔案不存在，這個函式會嘗試尋找並使用
    `config.example.json` 作為備用的設定來源。這樣做可以確保
    即使在沒有本地設定檔 (`config.json`) 的情況下，腳本也能以
    預設的範本設定繼續執行。

    Args:
        path: 設定檔的路徑，預設為 "config.json"。

    Returns:
        一個包含設定資訊的字典。

    Raises:
        FileNotFoundError: 如果 `config.json` 和 `config.example.json` 都不存在。
    """
    if not os.path.exists(path):
        alt_path = os.path.join(os.path.dirname(__file__), "config.example.json")
        if not os.path.exists(alt_path):
            raise FileNotFoundError("找不到設定檔 (config.json 或 config.example.json)。")

        print(f"[提示] 注意：正在使用範本設定檔 ({alt_path})")
        path = alt_path

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
