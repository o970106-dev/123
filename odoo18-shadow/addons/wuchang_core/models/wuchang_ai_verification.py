from odoo import models, fields

class WuchangAiVerification(models.Model):
    _name = 'wuchang.ai.verification'
    _description = 'Wuchang AI Verification'

    name = fields.Char(string='Verification ID', required=True)
    result = fields.Text(string='Verification Result')
    score = fields.Float(string='Confidence Score')
    is_verified = fields.Boolean(string='Is Verified', default=False)
