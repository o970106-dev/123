import os
import subprocess
import sys
import json
import time

def load_config(path="config.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def run_cmd(cmd):
    print(f">> 執行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"!! 錯誤: {e.stderr}")
        return False

def deploy_dns(domain, ip):
    print(f"=== 正在配置 Google Cloud DNS: {domain} ===")

    if not run_cmd("gcloud services enable dns.googleapis.com"):
        print("無法啟用 DNS API，請確認已安裝 gcloud 並具備權限。")
        return False

    zone_name = "wuchang-zone"
    zones = subprocess.run(f"gcloud dns managed-zones list --filter='dnsName:{domain}.' --format='value(name)'",
                           shell=True, capture_output=True, text=True).stdout.strip()

    if not zones:
        print(f"建立 Managed Zone: {zone_name}")
        run_cmd(f"gcloud dns managed-zones create {zone_name} --dns-name='{domain}.' --description='Wuchang Life DNS Zone'")
    else:
        zone_name = zones
        print(f"使用現有 Zone: {zone_name}")

    print("更新 DNS A 記錄...")
    run_cmd(f"gcloud dns record-sets transaction start --zone={zone_name}")
    subprocess.run(f"gcloud dns record-sets transaction remove --name='{domain}.' --ttl=300 --type=A --zone={zone_name}", shell=True, capture_output=True)
    subprocess.run(f"gcloud dns record-sets transaction remove --name='*.{domain}.' --ttl=300 --type=A --zone={zone_name}", shell=True, capture_output=True)

    run_cmd(f"gcloud dns record-sets transaction add {ip} --name='{domain}.' --ttl=300 --type=A --zone={zone_name}")
    run_cmd(f"gcloud dns record-sets transaction add {ip} --name='*.{domain}.' --ttl=300 --type=A --zone={zone_name}")

    if not run_cmd(f"gcloud dns record-sets transaction execute --zone={zone_name}"):
        print("DNS 交易執行失敗。")
        return False

    return True

def deploy_ssl(domain):
    print(f"=== 正在簽發 SSL 憑證 (Certbot + Google DNS): {domain} ===")

    run_cmd("sudo apt update")
    run_cmd("sudo apt install -y certbot python3-certbot-dns-google")

    email = f"admin@{domain}"
    cmd = (f"sudo certbot certonly --dns-google "
           f"--dns-google-propagation-seconds 90 "
           f"-d '{domain}' -d '*.{domain}' "
           f"--non-interactive --agree-tos --email {email}")

    if run_cmd(cmd):
        print(f"SSL 憑證簽發完成！憑證位於 /etc/letsencrypt/live/{domain}/")
        return True
    else:
        print("SSL 憑證簽發失敗。")
        return False

def main():
    start_time = time.time()
    cfg = load_config()
    ssh_cfg = cfg.get("ssh", {})

    domain = "wuchang.life"
    ip = ssh_cfg.get("host")
    if not ip or ip == "your.server.ip":
        print("[警告] config.json 中未設定有效的伺服器 IP，將跳過 DNS A 記錄更新。")
        ip = None

    dns_success = True
    if ip:
        dns_success = deploy_dns(domain, ip)

    if dns_success:
        deploy_ssl(domain)

    total_time = time.time() - start_time
    print(f"\n✅ 全自動 DNS 與 SSL 部署程序執行完畢。")
    print(f"⏱️ 總耗時: {total_time:.2f} 秒")
    print("請接續執行 enable_https.py 更新 Nginx 配置以啟用 HTTPS。")

if __name__ == "__main__":
    main()
