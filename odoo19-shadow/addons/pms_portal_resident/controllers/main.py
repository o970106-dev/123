from odoo import http
from odoo.http import request
try:
    from odoo.addons.pms_base.models.staps_core import staps_timed
except ImportError:
    def staps_timed(name):
        return lambda func: func

class ResidentPortal(http.Controller):
    @http.route(['/my/pms'], type='http', auth='user', website=True)
    @staps_timed("Resident Dashboard Load")
    def pms_dashboard(self, **kw):
        user = request.env.user
        coin_record = request.env['pms.happiness.coin'].sudo().search([('resident_id', '=', user.id)], limit=1)
        devices = request.env['pms.device'].search([('resident_id', '=', user.id)])

        values = {
            'user': user,
            'balance': coin_record.balance if coin_record else 0.0,
            'devices': devices,
        }
        return request.render('pms_portal_resident.dashboard_template', values)

    @http.route('/my/pms/device/toggle', type='json', auth='user', methods=['POST'])
    @staps_timed("Device Toggle CNS Broadcast")
    def toggle_device(self, device_id, **kw):
        device = request.env['pms.device'].browse(int(device_id))
        if device.resident_id.id != request.env.user.id:
            return {'status': 'error', 'message': 'Access denied'}

        new_state = 'off' if device.state == 'on' else 'on'
        device.write({'state': new_state})
        return {'status': 'success', 'new_state': new_state}
