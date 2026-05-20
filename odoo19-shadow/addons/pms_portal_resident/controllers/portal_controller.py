from odoo import http
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed

class PmsPortal(http.Controller):
    @http.route(['/my/pms'], type='http', auth="user", website=True)
    @staps_timed(persist=False)
    def pms_dashboard(self, **kw):
        user = request.env.user
        if hasattr(user, 'action_generate_google_token'):
            user.action_generate_google_token()

        # Pre-calculate data for Highest Degree Optimization
        devices = request.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
        coins = getattr(user, 'happiness_coin_balance', 0.0)

        # V3 Eco-Efficiency Algorithm
        total_devices = len(devices) if devices else 1
        eco_active = len([d for d in devices if d.eco_mode])
        variety = len(set([d.device_type for d in devices]))

        eco_efficiency_score = (
            (min(30, coins * 0.6)) +
            ((eco_active / total_devices) * 30) +
            (min(40, variety * 10))
        )

        values = {
            'devices': devices,
            'happiness_coin_balance': coins,
            'eco_efficiency_score': round(eco_efficiency_score, 1),
            'google_home_token': getattr(user, 'google_home_token', 'NOT_LINKED'),
        }

        return request.render("pms_portal_resident.portal_pms_dashboard", values)

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
        return {'status': 'success'}

    @http.route(['/pms/set_fan_speed'], type='json', auth="user")
    @staps_timed(persist=True)
    def set_fan_speed(self, device_id, fan_speed):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'status': 'error', 'message': 'Access Denied'}

        device.fan_speed = int(fan_speed)
        return {'status': 'success'}

    @http.route(['/pms/set_color_temp'], type='json', auth="user")
    @staps_timed(persist=True)
    def set_color_temp(self, device_id, color_temp):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'status': 'error', 'message': 'Access Denied'}

        device.color_temp = int(color_temp)
        return {'status': 'success'}

    @http.route(['/pms/toggle_eco_mode'], type='json', auth="user")
    @staps_timed(persist=True)
    def toggle_eco_mode(self, device_id, eco_state):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'status': 'error', 'message': 'Access Denied'}

        device.eco_mode = eco_state
        if eco_state:
            request.env.user.action_reward_sustainability(amount=2.0, reason="Eco Mode Optimization")
        return {'status': 'success'}

    @http.route(['/pms/claim_reward'], type='json', auth="user")
    @staps_timed(persist=True)
    def claim_reward(self):
        request.env.user.action_reward_sustainability(amount=5.0, reason="Portal Sustainability Claim")
        return {'status': 'success', 'new_balance': request.env.user.happiness_coin_balance}

    @http.route(['/pms/staps_ping'], type='json', auth="user")
    def staps_ping(self):
        from odoo.addons.pms_base.models.staps_core import get_staps_coordinate
        return {'status': 'success', 'coordinate': get_staps_coordinate('staps_ping')}
