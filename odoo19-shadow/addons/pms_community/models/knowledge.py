from odoo import models, fields, api
from odoo.addons.pms_base.pms_coordination import timed_process

class PmsKnowledge(models.Model):
    _name = 'pms.knowledge'
    _description = 'Property Management Knowledge Base'

    name = fields.Char(string='標題', required=True)
    category = fields.Selection([
        ('security', '安全管理'),
        ('maintenance', '設備維護'),
        ('finance', '財務透明'),
        ('service', '住戶服務'),
        ('regulation', '法規遵循')
    ], string='分類', default='service')
    content = fields.Text(string='內容')
    author_id = fields.Many2one('res.partner', string='作者', default=lambda self: self.env.user.partner_id)
    importance = fields.Selection([
        ('low', '普通'),
        ('medium', '重要'),
        ('high', '極高')
    ], string='重要性', default='medium')

    @timed_process("Knowledge Retrieval")
    def get_expert_advice(self, query):
        """
        AI Service Node (物管小J) logic to retrieve knowledge.
        """
        # In a real scenario, this would involve vector search or LLM integration.
        return self.search([('name', 'ilike', query)], limit=1)
