/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    console.log("PMS STAPS 2.0 Live Telemetry Initialized");

    const latencyEl = document.getElementById('staps_latency');
    const coordEl = document.getElementById('staps_coord');
    const heartbeatEl = document.getElementById('staps_heartbeat');

    // Simulate STAPS Heartbeat with nanosecond precision awareness
    function updateHeartbeat() {
        const start = performance.now();

        // Mocking a telemetry check
        setTimeout(() => {
            const end = performance.now();
            const latency = (end - start).toFixed(2);

            if (latencyEl) latencyEl.innerText = latency;
            if (heartbeatEl) {
                heartbeatEl.style.width = '100%';
                setTimeout(() => { heartbeatEl.style.width = '0%'; }, 500);
            }

            // Randomly update coordinate to simulate live activity
            if (coordEl) {
                const randomCoord = Math.random().toString(16).substring(2, 18);
                coordEl.innerText = randomCoord;
            }
        }, Math.random() * 200 + 50);
    }

    setInterval(updateHeartbeat, 5000);
    updateHeartbeat();

    // Toggle Device
    document.querySelectorAll('.pms-toggle').forEach(btn => {
        btn.addEventListener('click', async (ev) => {
            const deviceId = ev.currentTarget.dataset.id;
            try {
                const result = await rpc("/pms/device/toggle", { device_id: parseInt(deviceId) });
                if (result.success) {
                    window.location.reload();
                }
            } catch (err) {
                console.error("STAPS Telemetry Error:", err);
            }
        });
    });

    // Claim Reward
    const btnClaim = document.getElementById('btn_claim_reward');
    if (btnClaim) {
        btnClaim.addEventListener('click', async () => {
            try {
                const result = await rpc("/pms/claim_reward", {});
                if (result.success) {
                    alert("Sustainability Reward Claimed: 5.0 Coins!");
                    window.location.reload();
                } else {
                    alert(result.message || "Failed to claim reward.");
                }
            } catch (err) {
                console.error("STAPS Reward Error:", err);
            }
        });
    }

    // Sliders
    document.querySelectorAll('input[type="range"]').forEach(slider => {
        slider.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const value = ev.target.value;
            let route = "/pms/device/brightness";
            let params = { device_id: parseInt(deviceId), brightness: parseInt(value) };

            if (ev.target.classList.contains('pms-color-temp')) {
                route = "/pms/device/color_temp";
                params = { device_id: parseInt(deviceId), color_temp: parseInt(value) };
            } else if (ev.target.classList.contains('pms-fan-speed')) {
                route = "/pms/device/fan_speed";
                params = { device_id: parseInt(deviceId), fan_speed: parseInt(value) };
            }

            try {
                await rpc(route, params);
            } catch (err) {
                console.error("STAPS Update Error:", err);
            }
        });
    });

    // Eco Toggle
    document.querySelectorAll('.pms-eco-toggle').forEach(toggle => {
        toggle.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const checked = ev.target.checked;
            try {
                await rpc("/pms/device/eco", { device_id: parseInt(deviceId), eco_mode: checked });
            } catch (err) {
                console.error("STAPS Eco Error:", err);
            }
        });
    });
});
