import os

# 定義模組與對應的連接埠 (與 Nginx 配置同步)
MODULE_CONFIG = {
    "pm": {"port": 18101, "long_port": 8111},
    "pf": {"port": 18102, "long_port": 8112},
    "vt": {"port": 18103, "long_port": 8113},
    "cc": {"port": 18104, "long_port": 8114},
    "sc": {"port": 18105, "long_port": 8115},
    "er": {"port": 18107, "long_port": 8117},
}

COMPOSE_TEMPLATE = """version: "3.8"
services:
  db_{module}:
    image: postgres:15
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_DB=postgres
    volumes:
      - db_{module}-data:/var/lib/postgresql/data
    networks:
      - odoo_{module}_net
  odoo_{module}:
    image: odoo:19
    depends_on:
      - db_{module}
    restart: unless-stopped
    ports:
      - "{port}:8069"
      - "{long_port}:8072"
    environment:
      - ADMIN_PASSWORD=odoo
      - DB_HOST=db_{module}
      - DB_USER=odoo
      - DB_PASSWORD=odoo
    volumes:
      - odoo_{module}-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
    command: ["--db_host=db_{module}", "--db_user=odoo", "--db_password=odoo", "--addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons", "--proxy-mode", "--workers=0"]
    networks:
      - odoo_{module}_net
networks:
  odoo_{module}_net:
volumes:
  db_{module}-data:
  odoo_{module}-data:
"""

def main():
    print("=== 正在生成 PMS 模組 Docker Compose 檔案 (同步 Nginx 埠號) ===")
    for module, cfg in MODULE_CONFIG.items():
        port = cfg["port"]
        long_port = cfg["long_port"]
        target_dir = f"pms_modules/{module}/core/odoo19-shadow"
        os.makedirs(os.path.join(target_dir, "addons"), exist_ok=True)

        filepath = os.path.join(target_dir, "docker-compose.yml")
        content = COMPOSE_TEMPLATE.format(module=module, port=port, long_port=long_port)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[成功] 已生成: {filepath} (連接埠: {port})")

if __name__ == "__main__":
    main()
