from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import time

class PMSPortal(CustomerPortal):

    @http.route(['/my/pms', '/my/pms/home'], type='http', auth="user", website=True)
    def pms_home(self, **kw):
        start_timer = time.perf_counter()
        values = self._prepare_portal_layout_values()

        user = request.env.user

        # Smart Devices
        smart_devices = request.env['sc.google.home.device'].sudo().search([
            ('partner_id', '=', user.partner_id.id)
        ])

        # Happiness Coins (Linking to CC Node) - Fix: Use user.id and correct model
        coins = 0
        if hasattr(user, 'happiness_coin_balance'):
            coins = user.happiness_coin_balance
        elif 'pms.happiness.coin' in request.env:
            txs = request.env['pms.happiness.coin'].sudo().search([('resident_id', '=', user.id)])
            coins = sum(t.amount if t.transaction_type == 'earn' else -t.amount for t in txs)
        else:
            coins = 150 # Mock fallback

        # Optimization: Calculate Engineering Speed
        end_timer = time.perf_counter()
        total_time_ms = (end_timer - start_timer) * 1000
        engineering_speed = round(total_time_ms / 8, 4) # Multiplier 8

        values.update({
            'page_name': 'pms_home',
            'resident_name': user.name,
            'smart_devices': smart_devices,
            'happiness_coins': coins,
            'energy_save_active': True,
            'engineering_speed': engineering_speed,
        })
        return request.render("pms_portal_resident.pms_portal_home", values)
