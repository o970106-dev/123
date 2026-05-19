/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const speedVal = document.getElementById('staps_speed_val');
    if (speedVal) {
        setInterval(() => {
            const base = parseFloat(speedVal.innerText);
            const fluctuation = (Math.random() * 0.005) - 0.0025;
            const newVal = Math.max(0.0001, base + fluctuation).toFixed(4);
            speedVal.innerText = newVal + ' ms';
        }, 3000);
    }

    const energyToggle = document.getElementById('energySaveToggle');
    if (energyToggle) {
        energyToggle.addEventListener('change', function() {
            const isActive = this.checked;
            // Highest degree optimization: Trigger global energy saving and reward coins
            fetch('/my/pms/energy_save/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    params: { active: isActive }
                })
            }).then(response => response.json())
              .then(data => {
                  if (data.result && data.result.status === 'success') {
                      console.log("[STAPS] Global Energy Protocol Sync Complete. Reward granted.");
                      if (isActive) {
                          alert("Eco Mode Active! You've earned 5 Happiness Coins 🪙");
                          location.reload(); // Refresh to show new coin balance
                      }
                  }
              });
        });
    }

    const deviceBtns = document.querySelectorAll('.device-toggle-btn');
    deviceBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const deviceId = this.getAttribute('data-device-id');
            fetch('/my/pms/device/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ params: { device_id: deviceId } })
            }).then(res => res.json())
              .then(data => {
                  if (data.result && data.result.status === 'success') {
                      const badge = this.closest('.card-body').querySelector('.device-status-badge');
                      badge.innerText = data.result.state;
                      badge.className = 'badge device-status-badge ' + (data.result.state === 'ON' ? 'bg-warning text-dark' : 'bg-secondary');
                  }
              });
        });
    });
});
