#!/bin/bash
docker exec -u root odoo18-shadow-odoo18-1 odoo -i wuchang_core --test-enable -d wuchang_preview_20251107 --db_host=db18 --db_user=odoo --db_password=odoo --stop-after-init
