/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const latencyEl = document.getElementById('staps-latency');
    const indicatorEl = document.getElementById('latency-indicator');

    const updateLatency = async () => {
        const start = performance.now();
        try {
            const data = await jsonrpc('/pms/staps_ping', {});
            const end = performance.now();
            const latency = Math.round(end - start);

            if (latencyEl) latencyEl.innerText = `${latency}ms`;

            if (indicatorEl) {
                indicatorEl.className = 'latency-indicator';
                if (latency < 50) indicatorEl.classList.add('latency-green');
                else if (latency < 150) indicatorEl.classList.add('latency-yellow');
                else indicatorEl.classList.add('latency-red');
            }
        } catch (e) {
            console.error("STAPS Ping Failed", e);
        }
    };

    setInterval(updateLatency, 5000);
    updateLatency();

    // Device Toggles
    document.querySelectorAll('.device-toggle').forEach(btn => {
        btn.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.deviceId;
            await jsonrpc('/pms/toggle_device', { device_id: deviceId });
        });
    });

    // Brightness Sliders
    document.querySelectorAll('.brightness-slider').forEach(slider => {
        slider.addEventListener('change', async (ev) => {
            const deviceId = ev.target.dataset.deviceId;
            const val = ev.target.value;
            await jsonrpc('/pms/set_brightness', { device_id: deviceId, brightness: val });
        });
    });

    // Eco Mode Scene Toggles
    document.querySelectorAll('.eco-toggle').forEach(btn => {
        btn.addEventListener('click', async (ev) => {
            const deviceId = ev.currentTarget.dataset.deviceId;
            const res = await jsonrpc('/pms/toggle_eco_mode', { device_id: deviceId });
            if (res.status === 'success') {
                ev.currentTarget.classList.toggle('btn-primary', res.new_eco_mode);
                ev.currentTarget.classList.toggle('btn-outline-primary', !res.new_eco_mode);
            }
        });
    });

    // Reward Claim
    const claimBtn = document.getElementById('claim-reward');
    if (claimBtn) {
        claimBtn.addEventListener('click', async () => {
            const res = await jsonrpc('/pms/claim_reward', {});
            if (res.status === 'success') {
                const balEl = document.getElementById('coin-balance');
                if (balEl) balEl.innerText = res.new_balance.toFixed(2);
                alert('Sustainability Reward Claimed!');
            }
        });
    }
});
