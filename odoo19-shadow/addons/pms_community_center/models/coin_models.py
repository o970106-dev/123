from odoo import models, fields, api

class PmsHappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Happiness Coin Transaction'
    _order = 'date desc'

    user_id = fields.Many2one('res.users', string='Resident', required=True)
    amount = fields.Float(string='Amount', required=True)
    reason = fields.Char(string='Reason')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)

class ResUsers(models.Model):
    _inherit = 'res.users'

    happiness_coin_balance = fields.Float(string='Happiness Coin Balance', compute='_compute_coin_balance')
    eco_efficiency_score = fields.Float(string='Eco-Efficiency Score', compute='_compute_eco_score')
    google_home_token = fields.Char(string='Google Home Token')

    def _compute_coin_balance(self):
        # High-performance batch processing for Happiness Coin balance
        res = self.env['pms.happiness.coin'].read_group(
            [('user_id', 'in', self.ids)],
            ['amount:sum'],
            ['user_id']
        )
        mapped_data = {item['user_id'][0]: item['amount'] for item in res}
        for user in self:
            user.happiness_coin_balance = mapped_data.get(user.id, 0.0)

    def _compute_eco_score(self):
        """Weighted Eco-Efficiency Algorithm: 40% Coins, 40% Eco Mode, 20% Variety."""
        for user in self:
            devices = self.env['pms.device'].search([('resident_id', '=', user.id)])

            # 1. Coin Factor (max 40 pts, caps at 1000 coins)
            coin_pts = min((user.happiness_coin_balance / 1000.0) * 40.0, 40.0)

            # 2. Eco Mode Factor (max 40 pts)
            eco_devices = devices.filtered(lambda d: d.eco_mode)
            eco_pts = (len(eco_devices) / len(devices) * 40.0) if devices else 0.0

            # 3. Device Variety Factor (max 20 pts)
            types = set(devices.mapped('device_type'))
            variety_pts = min(len(types) * 5.0, 20.0)

            user.eco_efficiency_score = coin_pts + eco_pts + variety_pts

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True

    def action_generate_google_token(self):
        import secrets
        for user in self:
            if not user.google_home_token:
                user.google_home_token = secrets.token_hex(16)
