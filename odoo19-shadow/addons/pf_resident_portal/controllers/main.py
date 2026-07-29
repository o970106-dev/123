from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.pms_base.models.staps_core import staps_timed

class PMSPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        return values

    @http.route(['/my/pms', '/my/pms/home'], type='http', auth="user", website=True)
    @staps_timed(persist=True)
    def pms_home(self, **kw):
        values = self._prepare_portal_layout_values()

        unpaid_invoices = request.env['account.move'].sudo().search_count([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('payment_state', '!=', 'paid'),
            ('move_type', '=', 'out_invoice')
        ])
        fee_status = 'Pending' if unpaid_invoices > 0 else 'Paid'

        active_reservations = 0
        if 'pf.reservation' in request.env:
            active_reservations = request.env['pf.reservation'].sudo().search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', '=', 'confirmed')
            ])

        smart_devices = request.env['sc.google.home.device'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ])

        energy_data = {
            'today_usage': '12.5 kWh',
            'monthly_forecast': '380 kWh',
            'status': 'Normal'
        }

        # Fetch real Happiness Coin balance
        coin_balance = request.env['pms.happiness.coin'].sudo().get_balance(request.env.user.id)

        values.update({
            'page_name': 'pms_home',
            'user_id': request.env.user,
            'resident_name': request.env.user.name,
            'management_fee_status': fee_status,
            'happiness_coins': coin_balance,
            'google_home_token': request.env.user.google_home_token,
            'active_reservations': active_reservations,
            'unread_announcements': 3,
            'smart_devices': smart_devices,
            'energy_data': energy_data,
        })
        return request.render("pf_resident_portal.pms_portal_home", values)

    @http.route('/my/pms/device/toggle', type='json', auth="user", methods=['POST'], website=True)
    @staps_timed(persist=True)
    def toggle_device(self, device_id, state, **kw):
        device = request.env['sc.google.home.device'].sudo().browse(int(device_id))
        if device.exists() and device.partner_id.id == request.env.user.partner_id.id:
            device.sudo().write({'state_on': state})
            return {'status': 'success', 'new_state': state}
        return {'status': 'error', 'message': 'Access Denied'}

    @http.route('/my/pms/reward/sustainability', type='json', auth="user", methods=['POST'], website=True)
    @staps_timed(persist=True)
    def reward_sustainability(self, partner_id, **kw):
        if int(partner_id) == request.env.user.partner_id.id:
            # Reward 5 coins for sustainability
            request.env['pms.happiness.coin'].sudo().add_reward(request.env.user.id, 5, "Sustainability Reward")
            return {'status': 'success'}
        return {'status': 'error', 'message': 'Access Denied'}
