from odoo import http
from odoo import api
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed

class ResidentPortal(http.Controller):
    @http.route('/my/pms', type='http', auth='user', website=True)
    @staps_timed("dashboard_load", persist=True)
    def pms_dashboard(self, **kw):
        user = request.env.user
        devices = request.env['pms.device'].search([('resident_id', '=', user.id)])
        return request.render('pms_portal_resident.dashboard_template', {
            'user': user,
            'devices': devices,
        })

    @http.route('/my/pms/device/toggle', type='json', auth='user')
    @staps_timed("device_toggle", persist=True)
    def toggle_device(self, device_id, **kw):
        device = request.env['pms.device'].browse(device_id)
        if device.resident_id == request.env.user:
            new_state = 'off' if device.state == 'on' else 'on'
            device.write({'state': new_state})
            return {'status': 'success', 'new_state': new_state}
        return {'status': 'error', 'message': 'Permission Denied'}

    @http.route('/my/pms/claim_sustainability', type='json', auth='user')
    @staps_timed("claim_sustainability", persist=True)
    def claim_sustainability(self, **kw):
        user = request.env.user
        user.action_reward_sustainability()
        return {
            'status': 'success',
            'new_balance': user.happiness_coin_balance,
            'message': '5 Happiness Coins awarded!'
        }
