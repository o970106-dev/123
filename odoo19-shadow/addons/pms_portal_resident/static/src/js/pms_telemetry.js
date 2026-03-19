/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const latencyEl = document.getElementById('staps_latency');
    const coordEl = document.getElementById('staps_coord');
    const latencyBar = document.getElementById('latency_bar');

    // Simulate high-precision STAPS telemetry update
    const updateTelemetry = () => {
        const startTime = performance.now();
        rpc("/pms/staps_ping", {}).then((res) => {
            const duration = (performance.now() - startTime).toFixed(2);
            if (latencyEl) {
                latencyEl.innerText = duration;

                // STAPS Color Coding
                let statusClass = 'text-success';
                let barWidth = '10%';
                let barClass = 'bg-success';

                if (duration >= 150) {
                    statusClass = 'text-danger';
                    barWidth = '90%';
                    barClass = 'bg-danger';
                } else if (duration >= 50) {
                    statusClass = 'text-warning';
                    barWidth = '45%';
                    barClass = 'bg-warning';
                }

                latencyEl.className = `h4 ${statusClass}`;
                if (latencyBar) {
                    latencyBar.style.width = barWidth;
                    latencyBar.className = `progress-bar ${barClass}`;
                }
            }
            if (coordEl && res && res.coordinate) {
                coordEl.innerText = res.coordinate;
            }
        }).catch(() => {
             if (latencyEl) {
                latencyEl.innerText = 'OFFLINE';
                latencyEl.className = 'h4 text-danger';
             }
        });
    };

    setInterval(updateTelemetry, 5000);
    updateTelemetry();

    // Device Toggle Logic with Switch Interaction
    document.querySelectorAll('.pms-toggle-switch').forEach(toggle => {
        toggle.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const res = await rpc("/pms/toggle_device", { device_id: deviceId });
            if (res.status === 'success') {
                const tr = ev.target.closest('tr');
                const statusBadge = tr.querySelector('td span.badge');
                if (res.new_state) {
                    statusBadge.className = 'badge badge-success p-2';
                    statusBadge.innerText = 'ACTIVE';
                } else {
                    statusBadge.className = 'badge badge-secondary p-2';
                    statusBadge.innerText = 'INACTIVE';
                }
                console.log(`Device ${deviceId} toggled to ${res.new_state}`);
            } else {
                // Rollback switch if failed
                ev.target.checked = !ev.target.checked;
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
