import time
from odoo import http
from odoo.http import request
from odoo.addons.pms_base.pms_coordination import engine, timed_process

class ResidentPortal(http.Controller):

    @http.route(['/my/pms'], type='http', auth="user", website=True)
    @timed_process("Resident Portal Dashboard Load")
    def pms_dashboard(self, **kw):
        partner = request.env.user.partner_id

        # Simulate telemetry latency check
        start = time.perf_counter()
        engine.get_absolute_coordinate("portal_load")
        latency = (time.perf_counter() - start) * 1000 # ms

        devices = request.env['sc.google.home.device'].sudo().search([
            ('partner_id', '=', partner.id)
        ])

        # Mock management fee status
        # In real life, query account.move or similar
        management_fee_status = "已繳清"

        values = {
            'partner': partner,
            'devices': devices,
            'device_count': len(devices),
            'management_fee_status': management_fee_status,
            'latency': f"{latency:.4f}"
        }
        return request.render("pf_resident_portal.portal_pms_dashboard", values)
