# Taiji Hub Architecture & Runtime Audit

## A. Current Runtime Topology (Based on provided terminal trace)

The provided terminal trace from `/home/taiji_admin/Taiji_Hub` reveals the following runtime topology:
- **Environment**: Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-117-generic x86_64)
- **Primary Node**: `taiji01` Edge Runtime
- **Identity/Systemd User**: `taiji_admin`

**Active Services/Processes Detected:**
1.  **wuchang-gateway-9002.service**:
    -   **Type**: systemd user service (`~/.config/systemd/user/wuchang-gateway-9002.service`)
    -   **Directory**: `/home/taiji_admin/wuchang_8_0_core`
    -   **Command**: `exec python taiji_unified_gateway_edge.py`
    -   **Restart Policy**: `Restart=always` (RestartSec=5)
2.  **uvicorn Gateway (PID 309)**:
    -   **Command**: `/usr/bin/python3 -m uvicorn services.gateway.main:app --host 127.0.0.1 --port 9002`
    -   **Directory**: `/home/taiji_admin/Taiji_Hub`

**Repository Structure**:
-   `Taiji_Hub` contains `services/gateway/main.py`, `taiji_gateway.py`, `taiji_hub.py`, `w7tp_runtime/`, `W7TP_FIELD_ATLAS/`, `Taiji_Governance/`.
-   `wuchang_8_0_core` contains `taiji_unified_gateway_edge.py` and `wuchang_pos_voice_engine.py`.

## B. Duplicate Services & Overlapping Functionality

There are two distinct gateway processes attempting to provide similar routing/gateway functionality simultaneously:
1.  **Taiji Hub Gateway**: `services.gateway.main:app` (Running via `uvicorn` in `Taiji_Hub`).
2.  **Wuchang Edge Gateway**: `taiji_unified_gateway_edge.py` (Running via systemd service `wuchang-gateway-9002.service` in `wuchang_8_0_core`).

## C. Port Conflicts

**Critical Failure Point**: Port `9002` on `127.0.0.1`.
-   Process PID 309 (`services.gateway.main`) is currently bound to `127.0.0.1:9002`.
-   The systemd service `wuchang-gateway-9002.service` is configured to start `taiji_unified_gateway_edge.py`, which is also hardcoded/configured to bind to Port `9002`.

**The Restart Loop Mechanism**:
1.  `wuchang-gateway-9002.service` attempts to start.
2.  It fails with `address already in use` because PID 309 already holds port 9002.
3.  systemd applies `Restart=always` and waits 5 seconds.
4.  The cycle repeats indefinitely, leading to the observed `systemd restart counter exceeded 100+`.

## D. CPU Spikes & Ollama Wakeup Sources

**Why stopping wuchang-gateway-9002.service causes CPU usage to drop from ~100-158% to nearly idle:**
The continuous crashing and restarting of `taiji_unified_gateway_edge.py` via systemd creates a severe CPU overhead. Furthermore, every time `taiji_unified_gateway_edge.py` initializes (before it crashes on the port bind), it likely executes a **startup hook** or **warmup logic** that attempts to preload or ping the Ollama Local Model Server via `/api/chat` or `/api/generate`.

Because the service is restarting every 5 seconds:
1.  The startup script issues an HTTP request to `127.0.0.1:11434` to "warm up" the AI model.
2.  The Ollama runner receives the request and begins loading the ~5GB model into memory/GPU (causing WSL memory growth and 100-160% CPU on `ollama runner`).
3.  Simultaneously, the gateway script attempts to bind port 9002, fails, and exits.
4.  5 seconds later, the cycle repeats, forcing Ollama to continuously thrash memory and CPU attempting to serve interrupted warmup requests.

## E. Recommended Services to Keep

1.  **Keep**: `services.gateway.main` (Taiji Hub architecture). This appears to be the newer, modularized architecture (`Taiji_Hub` contains advanced structures like `services/gateway/topology_router.py`, `agent_dispatcher.py`, `policies/formal_tensor_validator.py`).
2.  **Keep**: `ollama.service`. The underlying model server is required, but it needs to be protected from restart loops.
3.  **Keep**: `taiji-03-ui.service` (OpenWebUI) assuming it routes through the primary gateway.

## F. Recommended Services to Remove (or Disable)

1.  **Disable/Remove**: `wuchang-gateway-9002.service` running `taiji_unified_gateway_edge.py`. This is the direct cause of the port conflict and the resulting CPU/Memory amplification loop.

## G. Safe Migration Sequence

1.  **Stop the offending loop**: `systemctl --user stop wuchang-gateway-9002.service`
2.  **Disable the service**: `systemctl --user disable wuchang-gateway-9002.service`
3.  **Verify Port 9002**: Ensure only PID 309 (`uvicorn services.gateway.main:app`) is listening on 9002.
4.  **Monitor Ollama**: Watch `ollama runner` CPU usage and WSL memory (vmmemWSL). They should normalize to idle baseline once the continuous warmup requests cease.
5.  **Re-route Traffic**: Ensure `taiji-03-ui.service` (OpenWebUI) is properly pointing to the active gateway (`services.gateway.main`).

## H. Risk Assessment

-   **High Risk (Current State)**: The continuous restart loop and model thrashing will eventually lead to Out-Of-Memory (OOM) kills within the WSL environment, destabilizing the entire Taiji01 edge node.
-   **Low Risk (Post-Cleanup)**: Disabling the older/duplicate edge gateway (`taiji_unified_gateway_edge.py`) resolves the port conflict instantly. As long as `services.gateway.main` provides feature parity, the system will stabilize with zero downtime to the unified architecture.
