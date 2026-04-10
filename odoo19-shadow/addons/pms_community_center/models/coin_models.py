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
    eco_efficiency_score = fields.Integer(string='Eco-Efficiency Score', compute='_compute_eco_score')

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
        """Compute score based on weighted algorithm: 40% Coins, 40% Eco Mode, 20% Variety."""
        for user in self:
            # 40% - Happiness Coin Balance (max 40 pts if balance >= 20)
            coin_pts = min(40, user.happiness_coin_balance * 2)

            # 40% - Eco Mode Active Status (max 40 pts)
            devices = self.env['pms.device'].search([('resident_id', '=', user.id)])
            eco_active_count = len(devices.filtered(lambda d: d.eco_mode))
            eco_pts = min(40, eco_active_count * 20) if devices else 0

            # 20% - Device Type Variety (max 20 pts)
            device_types = len(set(devices.mapped('device_type')))
            variety_pts = min(20, device_types * 5)

            user.eco_efficiency_score = int(coin_pts + eco_pts + variety_pts)

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True
