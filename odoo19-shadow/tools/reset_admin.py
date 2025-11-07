import odoo
from odoo import api, SUPERUSER_ID, sql_db
from odoo.service import server

DB_HOST = "db19"
DB_USER = "odoo"
DB_PASSWORD = "odoo"
DB_NAME = "wuchang_preview_20251107"
NEW_PASSWORD = "odoo"


def main():
    odoo.tools.config["db_host"] = DB_HOST
    odoo.tools.config["db_user"] = DB_USER
    odoo.tools.config["db_password"] = DB_PASSWORD
    odoo.tools.config["db_name"] = DB_NAME
    server.load_server_wide_modules()
    db = sql_db.db_connect(DB_NAME)
    with db.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        admin = env["res.users"].browse(2)
        admin.write({"password": NEW_PASSWORD})
        cr.commit()
    print("[ok] admin password reset for", DB_NAME)


if __name__ == "__main__":
    main()
