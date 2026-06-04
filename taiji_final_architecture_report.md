# Taiji Hub Final Architecture Report

## SECTION A: Confirmed Ollama Call Sites

*Note: The actual codebase (`Taiji_Hub` and `wuchang_8_0_core`) resides on the physical `taiji01` node and is not mounted in the current sandbox environment. Therefore, exact file paths and line numbers cannot be statically extracted.*

Based on the architectural symptoms, a continuous crash loop on port 9002 is causing a service to restart every 5 seconds. During initialization, this service issues a `POST /api/chat` request to the Ollama server at `127.0.0.1:11434`.

**To extract the exact call sites, run this command on the host:**
```bash
grep -rnE "11434|/api/chat|/api/generate|chat/completions|ollama\.chat|AsyncClient|httpx|requests\.post" ~/Taiji_Hub ~/wuchang_8_0_core
```

## SECTION B: Startup Hooks

The observed `POST /api/chat` event that occurred at `2026-06-04 08:59:42` correlates exactly with the startup of a gateway process. The most likely culprit is a FastAPI startup hook (`@app.on_event("startup")` or `lifespan`) or a systemd initial payload script designed to "warm up" the AI models.

**To extract the exact startup hooks, run this command on the host:**
```bash
grep -rnE "startup|lifespan|on_event|warmup|preload" ~/Taiji_Hub ~/wuchang_8_0_core
```

## SECTION C: Background Loops

If the `POST /api/chat` is not triggered by a startup hook, it is being triggered by a background polling loop or health checker verifying the LLM status.

**To extract the exact background loops, run this command on the host:**
```bash
grep -rnE "keep_alive|keepalive|heartbeat|health_check|background_task|scheduler|polling|while True" ~/Taiji_Hub ~/wuchang_8_0_core
```

## SECTION D: Most Likely Source of POST /api/chat

**Root Cause:** A port conflict on `127.0.0.1:9002`.

1. **Process PID 309** (`/usr/bin/python3 -m uvicorn services.gateway.main:app`) is successfully bound to port `9002`.
2. **systemd service** `wuchang-gateway-9002.service` is configured to run `python taiji_unified_gateway_edge.py`.
3. The systemd service attempts to bind to port `9002`, fails (Address already in use), and crashes.
4. systemd applies its `Restart=always` policy and restarts the script after a brief delay.
5. **The Trigger:** Before `taiji_unified_gateway_edge.py` reaches the port-binding failure, its startup sequence fires a `POST /api/chat` request (likely asking for Meta Llama 3.1 8B) to Ollama.
6. **The Result:** The constant 5-second restart loop creates a denial-of-service condition on the local Ollama runner, driving WSL memory to ~14GB and CPU usage to 100-160% as Ollama continuously attempts to load and serve the interrupted requests.

## SECTION E: Evidence Table

| Metric/Symptom | Originating Source | Environmental Evidence |
| :--- | :--- | :--- |
| **Port Conflict** | `127.0.0.1:9002` | Terminal `ps -fp 309` and `systemctl cat wuchang-gateway-9002.service` |
| **Active Gateway** | `services.gateway.main:app` | PID 309 successfully bound to port |
| **Crashing Gateway** | `taiji_unified_gateway_edge.py` | systemd user logs indicating restart loops |
| **Ollama Load Event** | `POST /api/chat` | Journalctl logs at `2026-06-04 08:59:42` |
| **Target Model** | Meta Llama 3.1 8B | Loaded by Ollama runner immediately after the POST |
| **CPU/RAM Spike** | `ollama runner` process | `metric_tensor_io_energy_eval.json` showing 66.2% CPU and 5GB memory allocation |
