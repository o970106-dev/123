import secrets
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Access Token', index=True)

    def action_generate_google_token(self):
        """Generate a secure random token for Google Home linking."""
        for user in self:
            if not user.google_home_token:
                user.google_home_token = secrets.token_hex(16)
