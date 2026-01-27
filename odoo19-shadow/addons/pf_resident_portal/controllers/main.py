from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class PMSPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # Add PMS related counters if needed
        return values

    @http.route(['/my/pms', '/my/pms/home'], type='http', auth="user", website=True)
    def pms_home(self, **kw):
        values = self._prepare_portal_layout_values()

        # Real logic: Fetch management fee status from account.move (Odoo Invoices)
        # We look for open invoices for the current partner
        unpaid_invoices = request.env['account.move'].sudo().search_count([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('payment_state', '!=', 'paid'),
            ('move_type', '=', 'out_invoice')
        ])
        fee_status = 'Pending' if unpaid_invoices > 0 else 'Paid'

        # Real logic: Fetch active reservations from pf.reservation (simulated model)
        active_reservations = 0
        if 'pf.reservation' in request.env:
            active_reservations = request.env['pf.reservation'].sudo().search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', '=', 'confirmed')
            ])

        # Advanced: Fetch resident's smart devices
        smart_devices = request.env['sc.google.home.device'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ])

        # Advanced: Mock energy data for the dashboard
        energy_data = {
            'today_usage': '12.5 kWh',
            'monthly_forecast': '380 kWh',
            'status': 'Normal'
        }

        values.update({
            'page_name': 'pms_home',
            'resident_name': request.env.user.name,
            'management_fee_status': fee_status,
            'active_reservations': active_reservations,
            'unread_announcements': 3,
            'smart_devices': smart_devices,
            'energy_data': energy_data,
        })
        return request.render("pf_resident_portal.pms_portal_home", values)
