# Architecture Inventory Report

## Executive Summary
An architecture discovery was initiated to identify the root causes of runtime symptoms including:
- WSL memory growth to ~14GB
- Ollama runner repeatedly launching and consuming 100-160% CPU
- Port conflicts (`127.0.0.1:9002`)
- High systemd restart counters

## Target Components
The investigation targeted the following components:
**Services:**
- `taiji-03-ui.service`
- `taiji-gateway.service`
- `wuchang-gateway-9002.service`
- `wuchang-v15-9090.service`
- `ollama.service`

**Processes/Scripts:**
- `taiji_unified_gateway_edge.py`
- `Wuchang_Universal_V15_DaemonAPI.py`
- `services.gateway.main`
- `openwebui_bridge`
- `open_webui`
- `ollama serve`

## Findings: Repository Discovery
An exhaustive search of the current repository (`Wuchang Community AI Infrastructure`) and the sandbox environment was performed.

### Missing Components
None of the targeted gateway services, scripts, or OpenWebUI/Ollama integration modules exist in the current repository. The search confirmed the absence of:
- `taiji_unified_gateway_edge.py`
- `Wuchang_Universal_V15_DaemonAPI.py`
- `taiji-03-ui.service`
- `taiji-gateway.service`
- `wuchang-gateway-9002.service`
- `wuchang-v15-9090.service`
- `ollama.service`
- `services.gateway.main`
- `runtime.openwebui_bridge`
- Any `open_webui` or `ollama` source code or docker-compose integration

### Current Repository Contents
The current repository primarily contains:
1. **Odoo Environments**: Docker Compose configurations for Odoo 18 (`odoo18-shadow`) and Odoo 19 (`odoo19-shadow`).
2. **Odoo Addons**: Custom Odoo modules such as `pos_beverage_modifier`, `pm3_integrated_property`, and `wuchang_property_governance_18`.
3. **Python Scripts**: Various scripts for POS menu management, beverage configuration, system updates (`manage_server.py`), and Odoo interaction (`odoo_jsonrpc.py`).
4. **Configuration**: Basic `.json` and `.conf` (Nginx) configuration files.

## Conclusion
The runtime stack under investigation (Taiji Gateway, Wuchang Universal Daemon API, OpenWebUI bridge, and Ollama integration) is **not deployed from this repository**.

These components likely reside in a different repository (e.g., a dedicated `Taiji_Hub` or `wuchang_8_0_core` repository) or a different branch that is currently not accessible. Further architectural analysis (dependency graphing, port conflict resolution, duplicate gateway detection) cannot be performed until the correct repository ownership and code locations are identified and provided.
