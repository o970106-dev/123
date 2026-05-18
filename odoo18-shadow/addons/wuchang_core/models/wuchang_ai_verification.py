from odoo import models, fields

class WuchangAiVerification(models.Model):
    _name = 'wuchang.ai.verification'
    _description = 'Wuchang AI Verification'

    name = fields.Char('Name', required=True)
