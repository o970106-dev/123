import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ResidentPortal(http.Controller):

    @http.route('/my/pms', type='http', auth='user', website=True)
    def pms_dashboard(self, **kwargs):
        user = request.env.user
        devices = request.env['pms.device'].search([('resident_id', '=', user.id)])

        values = {
            'coin_balance': user.happiness_coin_balance if hasattr(user, 'happiness_coin_balance') else 0,
            'devices': devices,
            'user_id': user
        }
        return request.render('pms_portal_resident.pms_dashboard_template', values)

    @http.route('/my/pms/device/toggle', type='json', auth='user', methods=['POST'])
    def toggle_device(self, device_id, **kwargs):
        device = request.env['pms.device'].search([('id', '=', int(device_id)), ('resident_id', '=', request.env.user.id)], limit=1)
        if not device:
            return {'status': 'error', 'message': 'Device not found'}

        new_state = not device.state
        device.write({'state': new_state})

        _logger.info(f"User {request.env.user.id} toggled device {device_id} to {new_state}")
        return {'status': 'success', 'new_state': new_state}
