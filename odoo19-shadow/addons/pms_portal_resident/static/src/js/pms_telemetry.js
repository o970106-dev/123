/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const latencyEl = document.getElementById('staps_latency');
    const coordEl = document.getElementById('staps_coord');

    // High-precision STAPS telemetry update
    const updateTelemetry = () => {
        const startTime = performance.now();
        rpc("/pms/staps_ping", {}).then((res) => {
            const endTime = performance.now();
            const duration = (endTime - startTime).toFixed(2);
            if (latencyEl) {
                latencyEl.innerText = duration;
                // Supreme Latency Thresholding (STAPS 2.0 Compliant)
                latencyEl.classList.remove('text-success', 'text-warning', 'text-danger');
                if (duration < 50) {
                    latencyEl.classList.add('text-success');
                } else if (duration < 150) {
                    latencyEl.classList.add('text-warning');
                } else {
                    latencyEl.classList.add('text-danger');
                }
            }
            if (coordEl && res && res.coordinate) {
                coordEl.innerText = res.coordinate;
            }
        }).catch(() => {
             const duration = (performance.now() - startTime).toFixed(2);
             if (latencyEl) {
                 latencyEl.innerText = duration;
                 latencyEl.classList.remove('text-success', 'text-warning');
                 latencyEl.classList.add('text-danger');
             }
        });
    };

    // Optimization: Polling every 5 seconds for real-time telemetry
    setInterval(updateTelemetry, 5000);
    updateTelemetry();

    // Device Toggle Logic with optimized DOM feedback
    document.querySelectorAll('.pms-toggle').forEach(btn => {
        btn.addEventListener('click', async (ev) => {
            const deviceId = ev.currentTarget.dataset.id;
            const res = await rpc("/pms/toggle_device", { device_id: deviceId });
            if (res.status === 'success') {
                const row = ev.currentTarget.closest('tr');
                const statusBadge = row.querySelector('td span.badge');
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

    // High-Precision Brightness Slider Logic
    document.querySelectorAll('.pms-brightness').forEach(slider => {
        slider.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const brightness = ev.target.value;
            await rpc("/pms/set_brightness", { device_id: deviceId, brightness: brightness });
        });
    });

    // Eco Mode Toggle Logic with Sustainability Rewards integration
    document.querySelectorAll('.pms-eco-toggle').forEach(toggle => {
        toggle.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.id;
            const ecoState = ev.target.checked;
            const res = await rpc("/pms/toggle_eco_mode", { device_id: deviceId, eco_state: ecoState });
            if (res.status === 'success' && ecoState) {
                // Refresh balance if needed or show feedback
                console.log("Sustainability reward granted for Eco Mode optimization.");
            }
        });
    });

    // Reward Claim Logic (Supreme UX)
    const claimBtn = document.getElementById('btn_claim_reward');
    if (claimBtn) {
        claimBtn.addEventListener('click', async () => {
            const res = await rpc("/pms/claim_reward", {});
            if (res.status === 'success') {
                const balanceDisplay = document.querySelector('.coin-balance-display .h1');
                if (balanceDisplay) {
                    balanceDisplay.innerText = res.new_balance;
                    // Visual feedback for reward claim
                    balanceDisplay.classList.add('animate__animated', 'animate__bounceIn');
                    setTimeout(() => balanceDisplay.classList.remove('animate__animated', 'animate__bounceIn'), 1000);
                }
            }
        });
    }
});
