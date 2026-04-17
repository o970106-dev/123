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
        """
        Compute Supreme Eco-Efficiency Score using a weighted 40/40/20 algorithm:
        - 40% Happiness Coins (Scaled)
        - 40% Active Eco-Mode Ratio
        - 20% Device Variety (Sustainable equipment usage)
        """
        for user in self:
            devices = self.env['pms.device'].search([('resident_id', '=', user.id)])
            total_devices = len(devices)

            # 1. Happiness Coin Component (Max 40 points)
            coin_points = min(40, user.happiness_coin_balance * 0.8)

            # 2. Eco-Mode Ratio Component (Max 40 points)
            eco_active = len(devices.filtered(lambda d: d.eco_mode))
            eco_points = (eco_active / total_devices * 40) if total_devices > 0 else 0

            # 3. Device Variety Component (Max 20 points)
            variety = len(set(devices.mapped('device_type')))
            variety_points = min(20, variety * 5)

            user.eco_efficiency_score = min(100, int(coin_points + eco_points + variety_points))

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True
