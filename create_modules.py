import os, pathlib, textwrap

mods = ['pm','pf','vt','cc','sc','er']
web_ports = {
    'pm':18101,'pf':18102,'vt':18103,'cc':18104,'sc':18105,'er':18107
}
lp_ports = {
    'pm':8111,'pf':8112,'vt':8113,'cc':8114,'sc':8115,'er':8117
}

for m in mods:
    base = pathlib.Path('/')/m/'core'/'odoo19-shadow'
    os.makedirs(base, exist_ok=True)
    for d in ['db-data','odoo-data','addons']:
        os.makedirs(base/d, exist_ok=True)
    compose = textwrap.dedent(f"""
    version: "3.8"
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
          - {m}net
      odoo19:
        image: odoo:19
        depends_on:
          - db19
        ports:
          - "{web_ports[m]}:8069"
          - "{lp_ports[m]}:8072"
        environment:
          - ADMIN_PASSWORD=odoo
          - DB_HOST=db19
          - DB_USER=odoo
          - DB_PASSWORD=odoo
          - HOST=db19
          - USER=odoo
          - PASSWORD=odoo
        volumes:
          - ./odoo-data:/var/lib/odoo
          - ./addons:/mnt/extra-addons
        command: ["--db_host=db19", "--db_user=odoo", "--db_password=odoo", "--addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons", "--proxy-mode", "--longpolling-port=8072", "--workers=2"]
        networks:
          - {m}net
    networks:
      {m}net:
    """
    )
    (base/'docker-compose.yml').write_text(compose)
    print(f'Wrote {base}/docker-compose.yml')

