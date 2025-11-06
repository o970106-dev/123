#!/usr/bin/env python3
import json
import paramiko
import sys

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def connect(cfg: dict) -> paramiko.SSHClient:
    host = cfg.get("host")
    port = int(cfg.get("port", 22))
    user = cfg.get("user")
    auth_method = cfg.get("auth_method", "key")
    key_path = cfg.get("key_path")
    password = cfg.get("password") or None

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if auth_method == "key":
        client.connect(
            hostname=host,
            port=port,
            username=user,
            key_filename=key_path if key_path else None,
            allow_agent=True,
            look_for_keys=True,
        )
    else:
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            allow_agent=False,
            look_for_keys=False,
        )
    return client

def upload_file(local_path: str, remote_path: str):
    cfg = load_config("config.json")
    client = connect(cfg)
    sftp = client.open_sftp()
    try:
        sftp.put(local_path, remote_path)
        print(f"[done] uploaded {local_path} -> {remote_path}")
    finally:
        sftp.close()
        client.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python upload_file.py <local_path> <remote_path>")
        sys.exit(1)
    
    upload_file(sys.argv[1], sys.argv[2])