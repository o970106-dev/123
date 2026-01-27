import os
from staps_core import STAPS_NODES, NODE_PORTS, NODE_LONG_PORTS, get_node_path, timed_process

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
    with timed_process("8 節點 Compose 檔案生成"):
        print("=== [STAPS] 正在同步 8 個地端神經適配器配置 ===")
        for module in STAPS_NODES:
            port = NODE_PORTS[module]
            long_port = NODE_LONG_PORTS[module]
            target_dir = get_node_path(module)
            os.makedirs(os.path.join(target_dir, "addons"), exist_ok=True)

            filepath = os.path.join(target_dir, "docker-compose.yml")
            content = COMPOSE_TEMPLATE.format(module=module, port=port, long_port=long_port)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[成功] 座標對齊: {module} -> Port {port}")

if __name__ == "__main__":
    main()
