from odoo import fields, models


class PM3BaseConfig(models.Model):
    _name = 'pm3.base.config'
    _description = 'PM3 Base Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    system_code = fields.Char(tracking=True)
    governance_mode = fields.Selection([
        ('community', 'Community Governance'),
        ('association', 'Association Governance'),
        ('mixed', 'Mixed Governance'),
    ], default='community', tracking=True)

    m5_policy_enabled = fields.Boolean(default=True, tracking=True)
    audit_fabric_enabled = fields.Boolean(default=True, tracking=True)
    ai_runtime_enabled = fields.Boolean(default=False, tracking=True)

    active = fields.Boolean(default=True)
