from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Access Token', index=True)
    eco_efficiency_score = fields.Float(string='Eco-Efficiency Score', compute='_compute_eco_score')

    def _compute_eco_score(self):
        """Compute Eco-Efficiency score based on device eco-mode and coins."""
        for user in self:
            base_score = user.happiness_coin_balance / 10.0
            devices = self.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
            eco_count = len(devices.filtered(lambda d: d.eco_mode))
            device_multiplier = 1.2 if eco_count > 0 else 1.0
            user.eco_efficiency_score = min(100.0, base_score * device_multiplier)
