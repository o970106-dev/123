from odoo import http
from odoo.http import request

class ResidentPortal(http.Controller):
    @http.route(['/my/pms'], type='http', auth="user", website=True)
    def pms_dashboard(self, **kw):
        # Collaboration Log data
        import json
        import os
        log_path = "/home/jules/collaboration_log.json"
        sync_state_path = "/home/jules/sync_state.json"
        collab_logs = []
        last_sync = "未知"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                collab_logs = json.load(f)[-5:] # Latest 5 entries

        if os.path.exists(sync_state_path):
            with open(sync_state_path, "r") as f:
                import datetime
                ls_time = json.load(f).get("last_sync_time", 0)
                if ls_time:
                    last_sync = datetime.datetime.fromtimestamp(ls_time).strftime('%Y-%m-%d %H:%M:%S')

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
            ],
            'collab_logs': collab_logs,
            'last_sync': last_sync
        }
        return request.render("pf_resident_portal.portal_my_pms", values)
