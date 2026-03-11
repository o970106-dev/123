/** @odoo-module **/
import { rpc } from "@web/core/network/rpc_service";
import { publicWidget } from "@web/legacy/js/public/public_widget";

publicWidget.registry.PMSTelemetry = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        'click .pms-device-toggle': '_onToggleClick',
        'click .action_sustainability': '_onClaimSustainability',
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
                if (result.new_state === 'on') {
                    $btn.removeClass('btn-info').addClass('btn-outline-light').text('TURN OFF');
                    $btn.closest('.pms-device-card').find('.rounded-circle').removeClass('bg-danger').addClass('bg-success');
                } else {
                    $btn.removeClass('btn-outline-light').addClass('btn-info').text('TURN ON');
                    $btn.closest('.pms-device-card').find('.rounded-circle').removeClass('bg-success').addClass('bg-danger');
                }
                this._addSTAPSLog("Device Toggle", duration);
            }
        } catch (error) {
            console.error("STAPS Sync Failed", error);
        } finally {
            $btn.prop('disabled', false);
        }
    },

    async _onClaimSustainability(ev) {
        const $btn = $(ev.currentTarget);
        const start = performance.now();

        try {
            const result = await rpc("/my/pms/claim_sustainability", {});
            const duration = (performance.now() - start).toFixed(4);

            if (result.status === 'success') {
                // Update balance in UI
                $('.display-4.text-warning').text(result.new_balance);
                this._addSTAPSLog("Sustainability Claim", duration);

                $btn.text('CLAIMED!').addClass('btn-success').removeClass('btn-outline-warning').prop('disabled', true);
            }
        } catch (error) {
            console.error("Sustainability Claim Failed", error);
        }
    },

    _addSTAPSLog(action, duration) {
        const coord = Math.random().toString(16).substring(2, 8);
        const newRow = `
            <tr>
                <td>${action}</td>
                <td class="text-success">${duration}ms</td>
                <td><code class="text-info small">${coord}...</code></td>
            </tr>
        `;
        $('#staps_log_body').prepend(newRow);
    }
});
