from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class ResidentPortal(CustomerPortal):

    @http.route(['/my/pms', '/my/pms/home'], type='http', auth="user", website=True)
    def pms_home(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("pf_resident_portal.portal_pms_home", values)

    def _prepare_home_portal_values(self, counters):
        values = super(ResidentPortal, self)._prepare_home_portal_values(counters)
        # Add PMS counters if needed
        return values
