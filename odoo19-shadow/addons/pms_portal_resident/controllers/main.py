from odoo import http
from odoo.http import request

class PMSPortalController(http.Controller):
    @http.route(['/my/pms'], type='http', auth='user', website=True)
    def pms_dashboard(self, **kw):
        user = request.env.user
        values = {
            'user': user,
            'happiness_coins': user.partner_id.happiness_coin_balance if hasattr(user.partner_id, 'happiness_coin_balance') else 0,
            'devices': request.env['pms.device'].search([]) if 'pms.device' in request.env else [],
        }
        return request.render('pms_portal_resident.pms_dashboard_template', values)

    @http.route('/my/pms/device/toggle', type='json', auth='user', csrf=False)
    def toggle_device(self, device_id, **kw):
        device = request.env['pms.device'].browse(int(device_id))
        if device.exists():
            new_state = not device.is_on
            device.write({'is_on': new_state})
            return {'status': 'success', 'new_state': 'on' if new_state else 'off'}
        return {'status': 'error', 'message': 'Device not found'}
