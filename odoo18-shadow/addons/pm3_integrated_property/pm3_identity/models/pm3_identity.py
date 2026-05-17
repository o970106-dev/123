from odoo import fields, models


class PM3Identity(models.Model):
    _name = 'pm3.identity'
    _description = 'PM3 Identity'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    sid = fields.Char(string='System Identity ID', required=True, copy=False, tracking=True)

    partner_id = fields.Many2one('res.partner', tracking=True)
    user_id = fields.Many2one('res.users', tracking=True)

    identity_type = fields.Selection([
        ('resident', 'Resident'),
        ('owner', 'Owner'),
        ('vendor', 'Vendor'),
        ('security', 'Security'),
        ('property_staff', 'Property Staff'),
        ('volunteer', 'Volunteer'),
        ('external_member', 'External Member'),
        ('visitor', 'Visitor'),
        ('ai_agent', 'AI Agent'),
        ('device', 'Device'),
    ], required=True, tracking=True)

    state = fields.Selection([
        ('basic_account', 'Basic Account'),
        ('identity_requested', 'Identity Requested'),
        ('pending_committee_review', 'Pending Committee Review'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
    ], default='basic_account', tracking=True)

    trust_level = fields.Integer(default=0, tracking=True)
    active = fields.Boolean(default=True)
