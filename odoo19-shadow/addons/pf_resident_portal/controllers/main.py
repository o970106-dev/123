from odoo import http
from odoo.http import request

class ResidentPortal(http.Controller):
    @http.route(['/my/pms'], type='http', auth="user", website=True)
    def pms_dashboard(self, **kw):
        # Mock data for demonstration
        values = {
            'resident_name': request.env.user.name,
            'fee_status': 'paid', # mock
            'smart_devices': [
                {'name': '客廳大燈', 'status': '開啟', 'icon': 'fa-lightbulb-o', 'class': 'text-warning'},
                {'name': '冷氣', 'status': '關閉', 'icon': 'fa-snowflake-o', 'class': 'text-info'},
                {'name': '門鎖', 'status': '已上鎖', 'icon': 'fa-lock', 'class': 'text-success'},
            ],
            'announcements': [
                {'date': '2025-01-25', 'title': '社區春節聚餐通知'},
                {'date': '2025-01-20', 'title': '電梯維護公告'},
            ]
        }
        return request.render("pf_resident_portal.portal_my_pms", values)
