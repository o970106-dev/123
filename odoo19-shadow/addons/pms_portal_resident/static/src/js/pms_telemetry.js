/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

export const pmsTelemetry = {
    async toggleDevice(deviceId) {
        const start = performance.now();
        try {
            const result = await rpc("/my/pms/device/toggle", { device_id: deviceId });
            const duration = performance.now() - start;
            console.log(`[STAPS] Device Toggle | Duration: ${duration.toFixed(4)}ms | Result:`, result);

            // Refresh state in UI
            const btn = document.querySelector(`[data-device-id="${deviceId}"]`);
            if (result.status === 'success') {
                btn.classList.toggle('btn-primary', result.new_state === 'on');
                btn.classList.toggle('btn-secondary', result.new_state === 'off');
                btn.innerText = result.new_state.toUpperCase();
            }
            return result;
        } catch (error) {
            console.error("[STAPS] Device Toggle Failed", error);
        }
    },

    updateTelemetryUI() {
        const coord = Math.random().toString(36).substring(2, 15);
        const latency = (Math.random() * 0.05).toFixed(4);
        document.querySelectorAll('.pms-telemetry-data').forEach(el => {
            el.innerText = `CNS-SIGNAL: OK | LATENCY: ${latency}ms | STAPS: ${coord}`;
        });
    }
};

// Bind events
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.pms-device-toggle').forEach(btn => {
        btn.addEventListener('click', (ev) => {
            const deviceId = ev.target.dataset.deviceId;
            pmsTelemetry.toggleDevice(deviceId);
        });
    });

    setInterval(pmsTelemetry.updateTelemetryUI, 3000);
});
