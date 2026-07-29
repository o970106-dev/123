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
        """Supreme Eco-Efficiency Scoring: Weighted algorithm."""
        for user in self:
            # 1. Happiness Coin Component (40% Weight)
            # Max 40 points for 20+ coins
            coin_points = min(40, int(user.happiness_coin_balance * 2))

            # 2. Active Eco Mode Component (40% Weight)
            # Max 40 points for 4+ devices in eco mode
            eco_count = self.env['pms.device'].search_count([
                ('resident_id', '=', user.id),
                ('eco_mode', '=', True)
            ])
            eco_points = min(40, eco_count * 10)

            # 3. Device Variety Bonus (20% Weight)
            # Reward diversity of smart home hardware
            device_types = self.env['pms.device'].read_group(
                [('resident_id', '=', user.id)],
                ['device_type'],
                ['device_type']
            )
            variety_points = min(20, len(device_types) * 5)

            user.eco_efficiency_score = coin_points + eco_points + variety_points

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True
