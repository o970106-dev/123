/** @odoo-module **/
import { rpc } from "@web/core/network/rpc_service";
import { publicWidget } from "@web/legacy/js/public/public_widget";

publicWidget.registry.PMSTelemetry = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        'click .pms-device-toggle': '_onToggleClick',
    },

    async _onToggleClick(ev) {
        const $btn = $(ev.currentTarget);
        const deviceId = $btn.data('device-id');
        const start = performance.now();

        $btn.prop('disabled', true).text('SYNCing...');

        try {
            const result = await rpc("/my/pms/device/toggle", { device_id: deviceId });
            const duration = (performance.now() - start).toFixed(4);

            if (result.status === 'success') {
                $btn.text(result.new_state.toUpperCase()).data('state', result.new_state);
                console.log(`[STAPSPF] Signal Sync | ${duration}ms | State: ${result.new_state}`);
            }
        } catch (error) {
            console.error("STAPS Sync Failed", error);
        } finally {
            $btn.prop('disabled', false);
        }
    }
});
