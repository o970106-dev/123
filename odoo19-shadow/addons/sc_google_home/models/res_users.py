import secrets
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Access Token', index=True)

    def action_generate_google_token(self):
        """Generates a secure, unique token for Google Home fulfillment."""
        for user in self:
            user.google_home_token = secrets.token_hex(16)
        return True
