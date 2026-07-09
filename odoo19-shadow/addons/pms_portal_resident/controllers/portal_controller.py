from odoo import http
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed

class PmsPortal(http.Controller):
    @http.route(['/my/pms'], type='http', auth="user", website=True)
    @staps_timed(persist=False)
    def pms_dashboard(self, **kw):
        return request.render("pms_portal_resident.portal_pms_dashboard")

    @http.route(['/pms/toggle_device'], type='json', auth="user")
    @staps_timed(persist=True)
    def toggle_device(self, device_id):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'status': 'error', 'message': 'Access Denied'}

        device.is_on = not device.is_on
        return {'status': 'success', 'new_state': device.is_on}

    @http.route(['/pms/set_brightness'], type='json', auth="user")
    @staps_timed(persist=True)
    def set_brightness(self, device_id, brightness):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'status': 'error', 'message': 'Access Denied'}

        device.brightness = int(brightness)
        return {'status': 'success', 'new_brightness': device.brightness}

    @http.route(['/pms/toggle_eco_mode'], type='json', auth="user")
    @staps_timed(persist=True)
    def toggle_eco_mode(self):
        user = request.env.user
        # Toggle eco_mode for all devices or a specific global state
        devices = request.env['pms.device'].search([('resident_id', '=', user.id)])
        new_state = not any(dev.eco_mode for dev in devices)
        for dev in devices:
            dev.eco_mode = new_state
            if new_state:
                dev.brightness = 50  # Auto-optimize for eco mode

        if new_state:
            user.action_reward_sustainability(amount=2.0, reason="Eco Mode Optimization")

        return {'status': 'success', 'eco_mode': new_state}

    @http.route(['/pms/claim_reward'], type='json', auth="user")
    @staps_timed(persist=True)
    def claim_reward(self):
        request.env.user.action_reward_sustainability(amount=5.0, reason="Portal Sustainability Claim")
        return {'status': 'success', 'new_balance': request.env.user.happiness_coin_balance}

    @http.route(['/pms/staps_ping'], type='json', auth="user")
    def staps_ping(self):
        from odoo.addons.pms_base.models.staps_core import get_staps_coordinate
        return {'status': 'success', 'coordinate': get_staps_coordinate('staps_ping')}
