from odoo import http
from odoo.http import request

class PmsCommunityController(http.Controller):

    @http.route(['/my/community/chat'], type='http', auth="user", website=True)
    def community_chat(self, **kw):
        messages = request.env['pms.community.chat'].sudo().search([
            ('district', '=', '仁義住宅區')
        ], limit=50)

        values = {
            'messages': messages,
            'district': '仁義住宅區'
        }
        return request.render("pms_community.portal_community_chat", values)

    @http.route(['/my/community/chat/send'], type='json', auth="user", website=True)
    def chat_send(self, message):
        if not message:
            return {'status': 'error'}

        msg = request.env['pms.community.chat'].sudo().post_message(message)
        return {
            'status': 'success',
            'author': msg.partner_id.name,
            'message': msg.message,
            'date': msg.create_date
        }

    @http.route(['/my/community/knowledge'], type='http', auth="user", website=True)
    def community_knowledge(self, **kw):
        articles = request.env['pms.knowledge'].sudo().search([])
        values = {
            'articles': articles
        }
        return request.render("pms_community.portal_community_knowledge", values)
