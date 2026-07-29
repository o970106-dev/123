from odoo import http
from odoo.http import request

class ResidentPortal(http.Controller):
    @http.route('/my/pms', type='http', auth='user', website=True)
    def pms_dashboard(self, **kw):
        user = request.env.user
        devices = request.env['pms.device'].search([('resident_id', '=', user.id)])
        return request.render('pms_portal_resident.dashboard_template', {
            'user': user,
            'devices': devices,
        })

    @http.route('/my/pms/device/toggle', type='json', auth='user')
    def toggle_device(self, device_id, **kw):
        device = request.env['pms.device'].browse(device_id)
        if device.resident_id == request.env.user:
            new_state = 'off' if device.state == 'on' else 'on'
            device.write({'state': new_state})
            return {'status': 'success', 'new_state': new_state}
        return {'status': 'error', 'message': 'Permission Denied'}
