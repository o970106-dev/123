from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class PMSPortal(CustomerPortal):

    @http.route(['/my/pms'], type='http', auth="user", website=True)
    def portal_my_pms(self, **kw):
        values = self._prepare_portal_layout_values()
        # Mock values for optimization demonstration
        values.update({
            'page_name': 'pms',
            'resident_name': request.env.user.name,
            'announcements': [], # Future: integrate with cc module
            'packages': [], # Future: integrate with pm module
        })
        return request.render("pf_resident_portal.portal_my_pms_dashboard", values)
