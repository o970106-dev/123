import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    console.log("PMS Highest Degree Telemetry Initialized");

    // STAPS Ping Logic
    const pingStaps = async () => {
        const start = performance.now();
        try {
            const data = await rpc('/pms/staps_ping', {});
            const end = performance.now();
            const latency = (end - start).toFixed(2);

            const latencyEl = document.getElementById('staps_latency');
            const heartbeatEl = document.getElementById('staps_heartbeat');
            const coordEl = document.getElementById('staps_coord');

            if (latencyEl) latencyEl.innerText = latency;
            if (heartbeatEl) heartbeatEl.style.width = Math.min(100, 100 - (latency / 10)) + '%';
            if (coordEl) coordEl.innerText = data.coordinate;
        } catch (e) {
            console.error("STAPS Telemetry Interrupted", e);
        }
    };

    setInterval(pingStaps, 5000);
    pingStaps();

    // Device Controls
    document.querySelectorAll('.pms-toggle').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const deviceId = e.currentTarget.dataset.id;
            const result = await rpc('/pms/toggle_device', { device_id: deviceId });
            if (result.status === 'success') {
                location.reload();
            }
        });
    });

    document.querySelectorAll('.pms-brightness').forEach(slider => {
        slider.addEventListener('change', async (e) => {
            const deviceId = e.target.dataset.id;
            const brightness = e.target.value;
            await rpc('/pms/set_brightness', { device_id: deviceId, brightness: brightness });
        });
    });

    document.querySelectorAll('.pms-eco-toggle').forEach(toggle => {
        toggle.addEventListener('change', async (e) => {
            const deviceId = e.target.dataset.id;
            const ecoState = e.target.checked;
            await rpc('/pms/toggle_eco_mode', { device_id: deviceId, eco_state: ecoState });
        });
    });

    // Reward System
    const btnClaim = document.getElementById('btn_claim_reward');
    if (btnClaim) {
        btnClaim.addEventListener('click', async () => {
            const result = await rpc('/pms/claim_reward', {});
            if (result.status === 'success') {
                const balanceEl = document.getElementById('coin_balance_val');
                if (balanceEl) balanceEl.innerText = result.new_balance;
                alert("Sustainability Reward Claimed!");
            } else {
                alert(result.message);
            }
        });
    }

    // Maintenance Submission
    const btnMaintenance = document.getElementById('btn_submit_maintenance');
    if (btnMaintenance) {
        btnMaintenance.addEventListener('click', async () => {
            const desc = document.getElementById('maintenance_desc').value;
            if (!desc) return alert("Please enter description");
            const result = await rpc('/pms/submit_maintenance', { description: desc });
            if (result.status === 'success') {
                alert("Maintenance Request Submitted to Matrix");
                location.reload();
            }
        });
    }

    // Volunteer Toggle
    const volunteerToggle = document.getElementById('volunteer_toggle');
    if (volunteerToggle) {
        volunteerToggle.addEventListener('change', async () => {
            const result = await rpc('/pms/toggle_volunteer', {});
            if (result.status === 'success') {
                alert(result.is_volunteer ? "Welcome to the Volunteer Nexus!" : "Volunteer status deactivated.");
                location.reload();
            }
        });
    }
});
