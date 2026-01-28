from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CommunityPortal(CustomerPortal):

    @http.route(['/my/happiness'], type='http', auth="user", website=True)
    def portal_my_happiness(self, **kw):
        values = self._prepare_portal_layout_values()
        templates = request.env['pms.voucher.template'].search([])
        values.update({
            'templates': templates,
            'page_name': 'happiness_mall',
        })
        return request.render("pms_portal_resident.portal_happiness_mall", values)

    @http.route(['/my/vouchers'], type='http', auth="user", website=True)
    def portal_my_vouchers(self, **kw):
        values = self._prepare_portal_layout_values()
        vouchers = request.env['pms.voucher'].search([('resident_id', '=', request.env.user.id)])
        values.update({
            'vouchers': vouchers,
            'page_name': 'my_vouchers',
        })
        return request.render("pms_portal_resident.portal_my_vouchers", values)

    @http.route(['/my/volunteer'], type='http', auth="user", website=True)
    def portal_my_volunteer(self, **kw):
        values = self._prepare_portal_layout_values()
        orders = request.env['pms.delivery.order'].search([('state', '=', 'pending')])
        values.update({
            'pending_orders': orders,
            'page_name': 'volunteer_hub',
        })
        return request.render("pms_portal_resident.portal_volunteer_hub", values)

    @http.route(['/my/happiness/purchase/<int:template_id>'], type='http', auth="user", methods=['POST'], website=True)
    def portal_happiness_purchase(self, template_id, **kw):
        template = request.env['pms.voucher.template'].browse(template_id)
        user = request.env.user
        if template.exists() and user.happiness_coin_balance >= template.coin_cost:
            # Create transaction
            request.env['pms.happiness.coin'].create({
                'resident_id': user.id,
                'amount': template.coin_cost,
                'transaction_type': 'spend',
                'description': f'Purchase of {template.name}'
            })
            # Create voucher
            request.env['pms.voucher'].create({
                'template_id': template.id,
                'resident_id': user.id,
            })
            return request.redirect('/my/vouchers')
        return request.redirect('/my/happiness?error=insufficient_funds')

    @http.route(['/my/volunteer/accept/<int:order_id>'], type='http', auth="user", methods=['POST'], website=True)
    def portal_volunteer_accept(self, order_id, **kw):
        order = request.env['pms.delivery.order'].browse(order_id)
        if order.exists() and order.state == 'pending':
            order.action_assign_volunteer(request.env.user.id)
            return request.redirect('/my/volunteer?status=accepted')
        return request.redirect('/my/volunteer?error=not_available')
