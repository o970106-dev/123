import pathlib

CONTENT = """version: "3.8"
services:
  db19:
    image: postgres:15
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_DB=postgres
    volumes:
      - ./db-data:/var/lib/postgresql/data
    networks:
      - odoo19net
  odoo19:
    image: odoo:19
    depends_on:
      - db19
    ports:
      - "18069:8069"
    environment:
      - ADMIN_PASSWORD=odoo
      - HOST=db19
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - ./odoo-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
    command: ["--db_host=db19", "--db_user=odoo", "--db_password=odoo", "--addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons"]
    networks:
      - odoo19net
networks:
  odoo19net:
"""

def main():
    path = pathlib.Path("/home/o0930/odoo19-shadow/docker-compose.yml")
    path.write_text(CONTENT, encoding="utf-8")
    print(f"Wrote {path}")

if __name__ == "__main__":
    main()

