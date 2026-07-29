import secrets
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Access Token', index=True)
    google_home_authorization_code = fields.Char(string='Google Home Authorization Code', index=True)

    def action_generate_google_token(self):
        """Generate a secure token for Google Home account linking."""
        for user in self:
            if not user.google_home_token:
                user.google_home_token = secrets.token_hex(16)
            if not user.google_home_authorization_code:
                user.google_home_authorization_code = secrets.token_hex(16)
        return True
