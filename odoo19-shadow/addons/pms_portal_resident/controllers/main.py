from odoo import http, fields
from odoo.http import request
import os

class PMSPortalController(http.Controller):
    @http.route(['/my/pms'], type='http', auth='user', website=True)
    def pms_dashboard(self, **kw):
        user = request.env.user
        devices = request.env['pms.device'].sudo().search([])
        # Simulated energy analytics
        energy_data = [12, 19, 3, 5, 2, 3, 9]

        values = {
            'user': user,
            'happiness_coins': user.happiness_coin_balance,
            'devices': devices,
            'energy_data': energy_data,
            'node_id': os.getenv('PMS_NODE_ID', 'PF-NODE'),
        }
        return request.render('pms_portal_resident.pms_dashboard_template', values)

    @http.route('/my/pms/device/toggle', type='json', auth='user', csrf=False)
    def toggle_device(self, device_id, **kw):
        device = request.env['pms.device'].sudo().browse(int(device_id))
        if device.exists():
            new_state = not device.is_on
            device.write({'is_on': new_state, 'last_update': fields.Datetime.now()})
            return {'status': 'success', 'new_state': 'on' if new_state else 'off'}
        return {'status': 'error', 'message': 'Device not found'}
