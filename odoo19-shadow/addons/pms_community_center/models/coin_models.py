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
        Compute Highest Degree Eco-Efficiency Score (V3 Weighted Algorithm):
        - 30% Happiness Coins (Sustainability Rewards)
        - 30% Eco-Mode Utilization (Active device management)
        - 40% Device Variety (Smart Home adoption - Priority)
        """
        # Batch search all devices for the requested users to avoid O(N^2)
        all_devices = self.env['pms.device'].sudo().search([('resident_id', 'in', self.ids)])
        device_map = {}
        for dev in all_devices:
            device_map.setdefault(dev.resident_id.id, []).append(dev)

        for user in self:
            # 1. Happiness Coin Weight (Max 30 points)
            coin_points = min(30, user.happiness_coin_balance * 0.6)

            # 2. Eco-Mode Weight (Max 30 points)
            user_devices = device_map.get(user.id, [])
            total_dev = len(user_devices)
            eco_dev = len([d for d in user_devices if d.eco_mode])
            eco_points = (eco_dev / total_dev * 30) if total_dev > 0 else 0

            # 3. Variety Weight (Max 40 points)
            unique_types = len(set(d.device_type for d in user_devices))
            variety_points = min(40, unique_types * 10)

            user.eco_efficiency_score = int(min(100, coin_points + eco_points + variety_points))

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True
