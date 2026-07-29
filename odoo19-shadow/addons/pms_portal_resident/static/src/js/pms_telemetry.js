/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const latencyEl = document.getElementById('staps_latency');
    const coordEl = document.getElementById('staps_coord');

    // Simulate high-precision STAPS telemetry update
    const updateTelemetry = () => {
        const startTime = performance.now();
        rpc("/pms/staps_ping", {}).then(() => {
            const duration = (performance.now() - startTime).toFixed(4);
            if (latencyEl) latencyEl.innerText = duration;
            if (coordEl) coordEl.innerText = Math.random().toString(36).substring(2, 10).toUpperCase();
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
