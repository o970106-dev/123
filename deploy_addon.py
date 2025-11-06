import argparse
import json
import os
import posixpath
from typing import Tuple

import paramiko


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

    if not host or not user:
        raise ValueError("配置不完整：需要 host 与 user")

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


def ensure_remote_dir(sftp: paramiko.SFTPClient, remote_path: str):
    parts = remote_path.strip("/").split("/")
    cur = "/"
    for p in parts:
        cur = posixpath.join(cur, p)
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def upload_dir(sftp: paramiko.SFTPClient, local_dir: str, remote_dir: str):
    ensure_remote_dir(sftp, remote_dir)
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir)
        rel = "" if rel == "." else rel.replace("\\", "/")
        target_dir = remote_dir if not rel else posixpath.join(remote_dir, rel)
        ensure_remote_dir(sftp, target_dir)
        for d in dirs:
            ensure_remote_dir(sftp, posixpath.join(target_dir, d))
        for fname in files:
            lpath = os.path.join(root, fname)
            rpath = posixpath.join(target_dir, fname)
            sftp.put(lpath, rpath)


def main():
    parser = argparse.ArgumentParser(description="部署 Odoo 附加元件到遠端 addons 路徑")
    parser.add_argument("--config", default="config.json", help="SSH 配置檔案路徑")
    parser.add_argument("--src", required=True, help="本地元件資料夾（如 pos_beverage_modifier）")
    parser.add_argument("--dest", required=True, help="遠端目標路徑（如 /opt/odoo17/odoo/addons/pos_beverage_modifier）")
    args = parser.parse_args()

    cfg = load_config(args.config)
    client = connect(cfg)
    sftp = client.open_sftp()
    try:
        upload_dir(sftp, args.src, args.dest)
        print(f"[done] uploaded {args.src} -> {args.dest}")
    finally:
        try:
            sftp.close()
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

