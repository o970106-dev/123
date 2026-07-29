import argparse
import json
import os
import sys
import time
from typing import Tuple

import paramiko


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        alt = os.path.join(os.path.dirname(__file__), "config.example.json")
        if not os.path.exists(alt):
            raise FileNotFoundError("缺少配置文件，請建立 config.json 或保留 config.example.json")
        path = alt
        print(f"[提示] 使用範例配置：{path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def connect(cfg: dict) -> paramiko.SSHClient:
    # 支持嵌套結構或扁平結構
    ssh_cfg = cfg.get("ssh", cfg)
    host = ssh_cfg.get("host")
    port = int(ssh_cfg.get("port", 22))
    user = ssh_cfg.get("user")
    auth_method = ssh_cfg.get("auth_method", "key")
    key_path = ssh_cfg.get("key_path")
    password = ssh_cfg.get("password") or None

    if not host or not user or host == "your.server.example":
        raise ValueError("配置不完整：需要 host 與 user (ssh 區段)")

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


def run_command(client: paramiko.SSHClient, command: str, sudo: bool = False, password: str = None) -> Tuple[str, str, int]:
    cmd = command
    if sudo:
        cmd = f"sudo -S -p '' {command}"
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        if password:
            stdin.write(password + "\n")
            stdin.flush()
    else:
        stdin, stdout, stderr = client.exec_command(cmd)

    out = stdout.read().decode(errors="ignore")
    err = stderr.read().decode(errors="ignore")
    rc = stdout.channel.recv_exit_status()
    return out, err, rc


def action_check(client: paramiko.SSHClient, password: str = None):
    print("[1/3] apt 更新索引...")
    out, err, rc = run_command(client, "apt update", sudo=True, password=password)
    print(out or err)

    print("\n[2/3] 可升級套件列表...")
    out, err, rc = run_command(client, "apt list --upgradable", sudo=False)
    print(out or err)

    print("\n[3/3] Ubuntu Pro / ESM 狀態...")
    out, err, rc = run_command(client, "pro status", sudo=True, password=password)
    print(out or err)


def action_upgrade(client: paramiko.SSHClient, password: str = None):
    print("[1/2] apt 更新索引...")
    out, err, rc = run_command(client, "apt update", sudo=True, password=password)
    print(out or err)

    print("\n[2/2] 執行升級 (apt upgrade -y)...")
    out, err, rc = run_command(client, "apt upgrade -y", sudo=True, password=password)
    print(out)
    if err:
        print(err)


def action_pro_status(client: paramiko.SSHClient, password: str = None):
    out, err, rc = run_command(client, "pro status", sudo=True, password=password)
    print(out or err)


def action_release_check(client: paramiko.SSHClient, password: str = None):
    out, err, rc = run_command(client, "do-release-upgrade -c", sudo=True, password=password)
    print(out or err)


def main():
    parser = argparse.ArgumentParser(description="遠端管理 Ubuntu 伺服器")
    parser.add_argument("action", choices=["check", "upgrade", "pro-status", "release-check", "run"], help="操作類型")
    parser.add_argument("--config", default="config.json", help="配置文件路徑，預設為 config.json")
    parser.add_argument("--cmd", help="當 action=run 時要執行的命令")
    parser.add_argument("--sudo", action="store_true", help="當 action=run 時以 sudo 執行")
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
        client = connect(cfg)
        ssh_cfg = cfg.get("ssh", cfg)
        password = ssh_cfg.get("password") or None

        if args.action == "check":
            action_check(client, password)
        elif args.action == "upgrade":
            action_upgrade(client, password)
        elif args.action == "pro-status":
            action_pro_status(client, password)
        elif args.action == "release-check":
            action_release_check(client, password)
        elif args.action == "run":
            if not args.cmd:
                print("請透過 --cmd 指定要執行的命令")
                sys.exit(2)
            out, err, rc = run_command(client, args.cmd, sudo=args.sudo, password=password)
            print(out)
            if err:
                print(err)
        else:
            print("未知操作")
    except Exception as e:
        print(f"[錯誤] {e}")
        sys.exit(1)
    finally:
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
