from odoo import http
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed

class PmsPortal(http.Controller):
    @http.route(['/my/pms'], type='http', auth="user", website=True)
    @staps_timed(persist=False)
    def pms_dashboard(self, **kw):
        if hasattr(request.env.user, 'action_generate_google_token'):
            request.env.user.action_generate_google_token()
        return request.render("pms_portal_resident.portal_pms_dashboard")

    @http.route(['/pms/toggle_device'], type='json', auth="user")
    @staps_timed(persist=True)
    def toggle_device(self, device_id):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'success': False, 'message': 'Access Denied'}

        device.is_on = not device.is_on
        return {'success': True, 'new_state': device.is_on}

    @http.route(['/pms/set_brightness'], type='json', auth="user")
    @staps_timed(persist=True)
    def set_brightness(self, device_id, brightness):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'success': False, 'message': 'Access Denied'}

        device.brightness = int(brightness)
        return {'success': True}

    @http.route(['/pms/set_fan_speed'], type='json', auth="user")
    @staps_timed(persist=True)
    def set_fan_speed(self, device_id, fan_speed):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'success': False, 'message': 'Access Denied'}

        device.fan_speed = int(fan_speed)
        return {'success': True}

    @http.route(['/pms/set_color_temp'], type='json', auth="user")
    @staps_timed(persist=True)
    def set_color_temp(self, device_id, color_temp):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'success': False, 'message': 'Access Denied'}

        device.color_temp = int(color_temp)
        return {'success': True}

    @http.route(['/pms/toggle_eco_mode'], type='json', auth="user")
    @staps_timed(persist=True)
    def toggle_eco_mode(self, device_id, eco_state):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'success': False, 'message': 'Access Denied'}

        device.eco_mode = eco_state
        if eco_state:
            request.env.user.action_reward_sustainability(amount=2.0, reason="Eco Mode Optimization")
        return {'success': True}

    @http.route(['/pms/claim_reward'], type='json', auth="user")
    @staps_timed(persist=True)
    def claim_reward(self):
        # 1-hour rate limiting for sustainability rewards
        from datetime import datetime, timedelta
        last_reward = request.env['pms.happiness.coin'].sudo().search([
            ('user_id', '=', request.env.user.id),
            ('date', '>', datetime.now() - timedelta(hours=1))
        ], limit=1)
        if last_reward:
            return {'success': False, 'message': 'Reward already claimed in the last hour.'}

        request.env.user.action_reward_sustainability(amount=5.0, reason="Portal Sustainability Claim")
        return {'success': True, 'new_balance': request.env.user.happiness_coin_balance}

    @http.route(['/pms/staps_ping'], type='json', auth="user")
    def staps_ping(self):
        from odoo.addons.pms_base.models.staps_core import get_staps_coordinate
        return {'status': 'success', 'coordinate': get_staps_coordinate('staps_ping')}

    @http.route(['/pms/toggle_volunteer'], type='json', auth="user")
    @staps_timed(persist=True)
    def toggle_volunteer(self):
        user = request.env.user
        user.x_is_volunteer = not user.x_is_volunteer
        if user.x_is_volunteer:
            user.action_reward_sustainability(amount=10.0, reason="Volunteer Onboarding")
        return {'success': True, 'is_volunteer': user.x_is_volunteer, 'new_balance': user.happiness_coin_balance}

    @http.route(['/pms/update_skills'], type='json', auth="user")
    @staps_timed(persist=True)
    def update_skills(self, skill_id):
        user = request.env.user
        skill = request.env['pms.skill'].browse(int(skill_id))
        if skill.exists():
            user.write({'x_volunteer_skills': [(4, skill.id)]})
        return {'success': True, 'skills': [{'id': s.id, 'name': s.name} for s in user.x_volunteer_skills]}
