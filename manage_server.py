import argparse
import sys
from typing import Tuple

import paramiko

from shared_config import load_config


def connect(config: dict) -> paramiko.SSHClient:
    ssh_config = config.get("ssh")
    if not ssh_config:
        raise ValueError("設定檔中缺少 `ssh` 區段。")

    host = ssh_config.get("host")
    port = int(ssh_config.get("port", 22))
    user = ssh_config.get("user")
    auth_method = ssh_config.get("auth_method", "key")
    key_path = ssh_config.get("key_path")
    password = ssh_config.get("password") or None

    if not host or not user:
        raise ValueError("SSH 設定不完整，`host` 和 `user` 為必填項。")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 尝试连接
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
        # 使用 -S 从 stdin 读取密码；-p '' 静默提示
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

    print("\n[2/3] 可升级软件包列表...")
    out, err, rc = run_command(client, "apt list --upgradable", sudo=False)
    print(out or err)

    print("\n[3/3] Ubuntu Pro / ESM 状态...")
    out, err, rc = run_command(client, "pro status", sudo=True, password=password)
    print(out or err)


def action_upgrade(client: paramiko.SSHClient, password: str = None):
    print("[1/2] apt 更新索引...")
    out, err, rc = run_command(client, "apt update", sudo=True, password=password)
    print(out or err)

    print("\n[2/2] 执行升级 (apt upgrade -y)...")
    out, err, rc = run_command(client, "apt upgrade -y", sudo=True, password=password)
    print(out)
    if err:
        print(err)


def action_pro_status(client: paramiko.SSHClient, password: str = None):
    out, err, rc = run_command(client, "pro status", sudo=True, password=password)
    print(out or err)


def action_release_check(client: paramiko.SSHClient, password: str = None):
    # 仅检查是否有可用发行版升级，不执行实际升级
    out, err, rc = run_command(client, "do-release-upgrade -c", sudo=True, password=password)
    print(out or err)


def main():
    parser = argparse.ArgumentParser(description="远程管理 Ubuntu 服务器")
    parser.add_argument("action", choices=["check", "upgrade", "pro-status", "release-check", "run"], help="操作类型")
    parser.add_argument("--config", default="config.json", help="配置文件路径，默认为 config.json")
    parser.add_argument("--cmd", help="当 action=run 时要执行的命令")
    parser.add_argument("--sudo", action="store_true", help="当 action=run 时以 sudo 执行")
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
        client = connect(cfg)
        password = cfg.get("password") or None

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
                print("请通过 --cmd 指定要执行的命令")
                sys.exit(2)
            out, err, rc = run_command(client, args.cmd, sudo=args.sudo, password=password)
            print(out)
            if err:
                print(err)
        else:
            print("未知操作")
    except Exception as e:
        print(f"[错误] {e}")
        sys.exit(1)
    finally:
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

