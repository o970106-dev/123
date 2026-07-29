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
        return {'status': 'success', 'brightness': device.brightness}

    @http.route(['/pms/toggle_eco_mode'], type='json', auth="user")
    @staps_timed(persist=True)
    def toggle_eco_mode(self):
        # Toggle Eco Mode for the resident (affects computation or specific devices)
        user = request.env.user
        # For simplicity, we toggle a flag on the user or find a 'Scene' device
        eco_scene = request.env['pms.device'].search([
            ('resident_id', '=', user.id),
            ('device_type', '=', 'action.devices.types.SCENE'),
            ('name', 'ilike', 'Eco')
        ], limit=1)

        if eco_scene:
            eco_scene.is_on = not eco_scene.is_on
            if eco_scene.is_on:
                user.action_reward_sustainability(amount=5.0, reason="Eco Mode Activated")
            return {'status': 'success', 'eco_mode': eco_scene.is_on}
        return {'status': 'error', 'message': 'Eco Mode Scene not found'}

    @http.route(['/pms/claim_reward'], type='json', auth="user")
    @staps_timed(persist=True)
    def claim_reward(self):
        request.env.user.action_reward_sustainability(amount=5.0, reason="Portal Sustainability Claim")
        return {'status': 'success', 'new_balance': request.env.user.happiness_coin_balance}

    @http.route(['/pms/staps_ping'], type='json', auth="user")
    def staps_ping(self):
        from odoo.addons.pms_base.models.staps_core import get_staps_coordinate
        return {'status': 'success', 'coordinate': get_staps_coordinate('staps_ping')}
