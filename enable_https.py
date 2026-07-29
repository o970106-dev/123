import os
import re

def update_nginx_config(filepath, domain_cert):
    if not os.path.exists(filepath):
        print(f"找不到檔案: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 將 listen 80 改為 listen 443 ssl
    # 2. 插入 SSL 憑證路徑
    # 3. 加入 80 -> 443 跳轉 (如果尚未存在)

    ssl_block = f"""    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/{domain_cert}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain_cert}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
"""

    # 簡單替換 listen 80; 為 ssl_block
    # 注意：這是一個簡化的實作，實際情況可能更複雜
    new_content = re.sub(r"listen\s+80;", ssl_block, content)

    # 建立 80 跳轉區塊
    server_names = re.findall(r"server_name\s+([^;]+);", content)
    redirect_blocks = ""
    for sn in set(server_names):
        redirect_blocks += f"""
server {{
    listen 80;
    server_name {sn.strip()};
    return 301 https://$host$request_uri;
}}
"""

    final_content = new_content + "\n" + redirect_blocks

    with open(filepath + ".ssl", "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"已生成 SSL 配置文件: {filepath}.ssl")

def main():
    domain = "wuchang.life"
    configs = ["nginx_wuchang.life.conf", "nginx_subdomains.conf"]

    for cfg in configs:
        update_nginx_config(cfg, domain)

    print("\nNginx SSL 配置生成完成。")
    print("請手動檢查並替換正式配置，然後重啟 Nginx：")
    print("sudo nginx -t && sudo systemctl restart nginx")

if __name__ == "__main__":
    main()
