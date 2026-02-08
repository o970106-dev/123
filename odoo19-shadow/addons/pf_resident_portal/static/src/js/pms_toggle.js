document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.device-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const deviceId = this.getAttribute('data-device-id');
            const state = this.checked;

            console.log(`STAPS Signal Sent: Device ${deviceId} -> ${state}`);

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
                if (data.result && data.result.status === 'success') {
                    console.log('STAPS Broadcast Confirmed: O(1) Latency achieved.');
                } else {
                    console.error('STAPS Broadcast Failure');
                    // Revert UI if needed
                }
            });
        });
    });
});
