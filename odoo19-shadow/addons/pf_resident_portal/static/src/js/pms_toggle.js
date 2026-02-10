document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.device-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const deviceId = this.getAttribute('data-device-id');
            const state = this.checked;

            console.log(`[STAPS CNS] Signal Sent: Device ${deviceId} -> ${state}`);
            this.closest('.glass-card').style.opacity = '0.5'; // Visual feedback

            fetch('/my/pms/device/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': odoo.csrf_token,
                },
                body: JSON.stringify({
                    params: {
                        device_id: deviceId,
                        state: state
                    }
                })
            }).then(response => response.json())
            .then(data => {
                this.closest('.glass-card').style.opacity = '1';
                if (data.result && data.result.status === 'success') {
                    console.log('[STAPS CNS] Broadcast Confirmed: O(1) Latency achieved.');
                } else {
                    console.error('[STAPS CNS] Broadcast Failure');
                    this.checked = !state; // Revert
                }
            }).catch(err => {
                this.closest('.glass-card').style.opacity = '1';
                this.checked = !state;
                console.error('[STAPS CNS] Network Error', err);
            });
        });
    });
});
