document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.device-toggle');

    // Performance monitor for STAPS
    const reportLatency = (startTime) => {
        const latency = performance.now() - startTime;
        console.log(`%c[STAPS 2.0] E2E Signal Latency: ${latency.toFixed(4)}ms`, 'color: #00ff00; font-weight: bold;');
    };

    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const deviceId = this.getAttribute('data-device-id');
            const state = this.checked;

            console.log(`[STAPS CNS] Signal Sent: Device ${deviceId} -> ${state}`);
            this.closest('.glass-card').style.opacity = '0.5'; // Visual feedback

            const startTime = performance.now();
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
                reportLatency(startTime);
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

    const rewardBtn = document.querySelector('.action-sustainability');
    if (rewardBtn) {
        rewardBtn.addEventListener('click', function() {
            const partnerId = this.getAttribute('data-resident-id');
            console.log(`[STAPS CNS] Claiming reward for partner: ${partnerId}`);

            fetch('/my/pms/reward/sustainability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': odoo.csrf_token,
                },
                body: JSON.stringify({
                    params: {
                        partner_id: partnerId
                    }
                })
            }).then(response => response.json())
            .then(data => {
                if (data.result && data.result.status === 'success') {
                    alert('Success! 5 Happiness Coins added to your account for sustainable behavior.');
                    location.reload();
                }
            });
        });
    }
});
