/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";
import { Component, onMounted } from "@odoo/owl";

export const pmsTelemetry = {
    async toggleDevice(deviceId) {
        const start = performance.now();
        try {
            const result = await rpc("/my/pms/device/toggle", { device_id: deviceId });
            const duration = performance.now() - start;
            console.log(`[STAPS] Device Toggle | Duration: ${duration.toFixed(4)}ms | Result:`, result);
            return result;
        } catch (error) {
            console.error("[STAPS] Device Toggle Failed", error);
        }
    },

    updateDashboard() {
        // Mock update for telemetry
        const coord = Math.random().toString(36).substring(7);
        document.querySelectorAll('.pms-telemetry-badge').forEach(el => {
            el.innerText = `CNS-SIGNAL: OK | LATENCY: 0.02ms | STAPS: ${coord}`;
        });
    }
};

// Global export for legacy template compatibility
window.pmsTelemetry = pmsTelemetry;

// Auto-update dashboard telemetry every 5 seconds
setInterval(pmsTelemetry.updateDashboard, 5000);
