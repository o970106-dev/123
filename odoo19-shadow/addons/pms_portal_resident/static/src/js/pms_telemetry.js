/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const latencyEl = document.getElementById('staps_latency');
    const coordEl = document.getElementById('staps_coord');

    // Simulate high-precision STAPS telemetry update
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
            } else if (coordEl) {
                coordEl.innerText = Math.random().toString(36).substring(2, 10).toUpperCase();
            }
        }).catch(() => {
             const duration = (performance.now() - startTime).toFixed(4);
             if (latencyEl) latencyEl.innerText = duration;
        });
    };

    setInterval(updateTelemetry, 5000);
    updateTelemetry();

    // Device Toggle Logic with Dynamic DOM updates
    document.querySelectorAll('.pms-toggle').forEach(btn => {
        btn.addEventListener('click', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const res = await rpc("/pms/toggle_device", { device_id: deviceId });
            if (res.status === 'success') {
                const statusBadge = ev.target.closest('tr').querySelector('td span.badge');
                if (res.new_state) {
                    statusBadge.className = 'badge badge-success';
                    statusBadge.innerText = 'ON';
                } else {
                    statusBadge.className = 'badge badge-secondary';
                    statusBadge.innerText = 'OFF';
                }
                console.log(`Device ${deviceId} toggled to ${res.new_state}`);
            }
        });
    });

    // Brightness Slider Logic
    document.querySelectorAll('.pms-brightness').forEach(slider => {
        slider.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const brightness = ev.target.value;
            const res = await rpc("/pms/set_brightness", { device_id: deviceId, brightness: brightness });
            if (res.status === 'success') {
                console.log(`Device ${deviceId} brightness set to ${brightness}`);
            }
        });
    });

    // Eco Mode Toggle Logic
    const ecoToggle = document.getElementById('pms_eco_mode_toggle');
    if (ecoToggle) {
        ecoToggle.addEventListener('change', async (ev) => {
            const res = await rpc("/pms/toggle_eco_mode", { enabled: ev.target.checked });
            if (res.status === 'success') {
                console.log(`Eco Mode toggled to ${ev.target.checked}`);
                location.reload(); // Reload to update score and status
            }
        });
    }

    // Reward Claim Logic
    const claimBtn = document.getElementById('btn_claim_reward');
    if (claimBtn) {
        claimBtn.addEventListener('click', async () => {
            const res = await rpc("/pms/claim_reward", {});
            if (res.status === 'success') {
                alert(`Reward Claimed! New Balance: ${res.new_balance} Coins`);
                const balanceDisplay = document.querySelector('.coin-balance-display .h1');
                if (balanceDisplay) balanceDisplay.innerText = res.new_balance;
            }
        });
    }
});
