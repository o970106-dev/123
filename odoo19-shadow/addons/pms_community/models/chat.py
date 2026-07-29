from odoo import models, fields, api

class PmsCommunityChat(models.Model):
    _name = 'pms.community.chat'
    _description = 'Renyi District Community Chat'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', string='發言者', required=True, default=lambda self: self.env.user.partner_id)
    message = fields.Text(string='訊息內容', required=True)
    district = fields.Char(string='社區區域', default='仁義住宅區')
    is_ai_response = fields.Boolean(string='AI 回應', default=False)

    @api.model
    def post_message(self, message):
        """
        Post a message to the community chat and trigger AI response if needed.
        """
        new_msg = self.create({'message': message})
        if "小J" in message or "問問" in message:
            # Simulate AI behavior
            response = f"您好！我是您的物管助手小J。針對您的問題「{message}」，我正在查閱知識庫..."
            self.create({
                'message': response,
                'is_ai_response': True,
                'partner_id': self.env.ref('base.partner_root').id # Use admin or system partner
            })
        return new_msg
