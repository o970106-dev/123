import secrets
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Access Token', index=True)
    google_home_authorization_code = fields.Char(string='Google Home Auth Code', index=True)
    google_home_refresh_token = fields.Char(string='Google Home Refresh Token', index=True)

    def action_generate_google_token(self):
        """Generate secure tokens for Google Home account linking."""
        for user in self:
            if not user.google_home_token:
                user.google_home_token = secrets.token_hex(32)
            if not user.google_home_refresh_token:
                user.google_home_refresh_token = secrets.token_hex(32)
        return True
