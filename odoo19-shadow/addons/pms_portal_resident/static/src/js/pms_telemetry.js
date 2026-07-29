/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const latencyEl = document.getElementById('staps_latency');
    const coordEl = document.getElementById('staps_coord');

    // High-precision STAPS telemetry update
    const updateTelemetry = () => {
        const startTime = performance.now();
        rpc("/pms/staps_ping", {}).then((res) => {
            const duration = (performance.now() - startTime).toFixed(4);
            if (latencyEl) {
                latencyEl.innerText = duration;
                latencyEl.className = duration < 50 ? 'text-success' : (duration < 150 ? 'text-warning' : 'text-danger');
            }
            if (coordEl && res && res.coordinate) {
                coordEl.innerText = res.coordinate;
            }
        }).catch(() => {
             const duration = (performance.now() - startTime).toFixed(4);
             if (latencyEl) latencyEl.innerText = duration;
        });
    };

    setInterval(updateTelemetry, 5000);
    updateTelemetry();

    // Device Toggle Logic
    document.querySelectorAll('.pms-toggle').forEach(btn => {
        btn.addEventListener('click', async (ev) => {
            const deviceId = ev.currentTarget.dataset.id;
            const res = await rpc("/pms/toggle_device", { device_id: deviceId });
            if (res.status === 'success') {
                const statusBadge = ev.currentTarget.closest('tr').querySelector('td span.badge');
                if (res.new_state) {
                    statusBadge.className = 'badge badge-success px-3 py-2';
                    statusBadge.innerText = 'ON';
                } else {
                    statusBadge.className = 'badge badge-secondary px-3 py-2';
                    statusBadge.innerText = 'OFF';
                }
            }
        });
    });

    // Brightness Slider Logic
    document.querySelectorAll('.pms-brightness').forEach(slider => {
        slider.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const brightness = ev.target.value;
            await rpc("/pms/set_brightness", { device_id: deviceId, brightness: brightness });
        });
    });

    // Eco Mode Toggle Logic
    document.querySelectorAll('.pms-eco-toggle').forEach(toggle => {
        toggle.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const ecoState = ev.target.checked;
            await rpc("/pms/toggle_eco_mode", { device_id: deviceId, eco_state: ecoState });
        });
    });

    // Reward Claim Logic
    const claimBtn = document.getElementById('btn_claim_reward');
    if (claimBtn) {
        claimBtn.addEventListener('click', async () => {
            const res = await rpc("/pms/claim_reward", {});
            if (res.status === 'success') {
                const balanceDisplay = document.querySelector('.coin-balance-display .h1');
                if (balanceDisplay) balanceDisplay.innerText = res.new_balance;
            }
        });
    }
});
