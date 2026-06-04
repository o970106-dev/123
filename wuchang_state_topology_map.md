# Wuchang Repository State Topology Map

## 1. Authority Field
- **Nginx Configuration**: `nginx_wuchang.life.conf`, `www_redirect_443.conf`, `nginx_subdomains.conf` define the entry points and proxy routing authority to backend services.
- **System Management**: `manage_server.py`, `connect.ps1`, `deploy_wuchang.ps1` manage deployment and environment execution authority.

## 2. Service Field
- **Odoo 18 Runtime**: Configured in `odoo18-shadow/docker-compose.yml`. Provides the core business logic service.
- **Odoo 19 Runtime**: Configured in `odoo19-shadow/docker-compose*.yml`. Represents an experimental or next-gen service tier.
- **PostgreSQL Database**: Deployed alongside Odoo runtimes as the persistence service.

## 3. Data Field
- **Static Seed Data**: `main_items.csv`, `main_items.json`, `menu_addon_mapping.csv`, `menu_addon_unique.json`.
- **Payload Data**: `menu_payload_m.json`, `menu_payload_m_combo.json` represent structured data states to be injected into the Service Field.
- **Backup Archives**: `backups/` directory holds historical state snapshots.

## 4. Governance Field
- **Odoo Modules**: `pos_beverage_modifier/`, `pm3_integrated_property/`, `wuchang_property_governance_18/` dictate the business rules, security models, and access control within the Odoo ecosystem.
- **Data Integrity Validation**: `verify_index.py`, `verify_beverage_variants.py`, `check_pos_status.py` govern the correctness of the Data Field upon injection.

## 5. Runtime Field
- **Execution Engine**: Docker and Docker Compose (managing Odoo and PostgreSQL containers).
- **API Interaction Layer**: `odoo_jsonrpc.py` provides the runtime interface for interacting with the Odoo API.

## 6. Event Propagation Field
- **State Injection Scripts**: `import_pos_menu.py`, `import_main_items.py`, `load_main_items.py` propagate static data into the live Odoo database.
- **Configuration Events**: `create_beverage_config.py`, `seed_beverage_config.py`, `configure_beverage_attributes.py` propagate setup events.
- **Session Events**: `open_pos_session.py`, `close_all_pos_sessions.py` trigger operational state changes within the POS application.

## 7. Failure Propagation Field
- **API Failures**: If `odoo_jsonrpc.py` or the underlying Odoo container fails, all state injection and session management scripts (`import_pos_menu.py`, etc.) will fail to propagate state.
- **Data Malformation**: Corrupt data in the Data Field (`menu_addon_mapping.json`) will propagate failure into the Service Field during execution of Event Propagation scripts.
- **Database Connection**: PostgreSQL container crashes propagate failure to the Odoo service containers, rendering the entire Service Field inaccessible.

## 8. Execution Topology
`[Data Field (CSV/JSON/XML)] -> [Event Propagation Field (Python Scripts using odoo_jsonrpc)] -> [Authority Field (Nginx/Docker)] -> [Runtime Field (Odoo container)] -> [Governance Field (Odoo Addons)] -> [Service Field (PostgreSQL)]`

---

*Note: This topology maps only the components present within the `Wuchang Community AI Infrastructure` repository. It does not include the Taiji_Hub gateway, OpenWebUI, or Ollama runtimes, as those states exist outside of this field.*
