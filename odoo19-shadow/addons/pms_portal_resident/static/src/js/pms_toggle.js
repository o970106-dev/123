/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const toggles = document.querySelectorAll('.device-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('click', async (ev) => {
            const deviceId = ev.target.dataset.id;
            try {
                const result = await jsonrpc('/my/pms/device/toggle', {
                    device_id: deviceId,
                });
                if (result.status === 'success') {
                    // Update UI state
                    ev.target.parentElement.querySelector('span').textContent = result.new_state;
                    if (result.new_state === 'off') {
                        ev.target.classList.add('device-off');
                    } else {
                        ev.target.classList.remove('device-off');
                    }
                } else {
                    alert(result.message || 'Error toggling device');
                }
            } catch (err) {
                console.error('Toggle failed', err);
            }
        });
    });
});
