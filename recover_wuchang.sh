#!/bin/bash
# Wuchang Core Recovery Script

echo "Starting Wuchang OS recovery..."

# 1. Start the containers
cd odoo18-shadow
docker-compose up -d

# 2. Wait for Odoo to be ready
echo "Waiting for Odoo to initialize..."
sleep 10

# 3. Update the wuchang_core module to rebuild registry
# Replace 'postgres' with your actual database name if different
DB_NAME=${1:-postgres}
docker exec -u odoo wuchang_os_odoo_18 odoo -u wuchang_core -d $DB_NAME --stop-after-init

echo "Recovery complete. Registry should be stable."
