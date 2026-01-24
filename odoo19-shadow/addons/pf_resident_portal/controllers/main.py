from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class PMSPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # Add PMS count if needed
        return values

    @http.route(['/my/pms'], type='http', auth="user", website=True)
    def portal_my_pms(self, **kw):
        values = self._prepare_portal_layout_values()
        # Mock values for optimization demonstration
        values.update({
            'page_name': 'pms',
            'resident_name': request.env.user.name,
            'announcements': [
                {'title': '年度大樓外牆清洗通知', 'date': '2026-02-01'},
                {'title': '管委會會議紀錄已公開', 'date': '2026-01-20'}
            ],
            'packages': [
                {'id': 'PKG001', 'carrier': '順豐速運', 'status': '待領取'},
                {'id': 'PKG002', 'carrier': '黑貓宅急便', 'status': '已領取'}
            ],
        })
        return request.render("pf_resident_portal.portal_my_pms_dashboard", values)
