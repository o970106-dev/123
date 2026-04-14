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
        Supreme Eco-Efficiency Algorithm (40/40/20 Weighted):
        - 40% Happiness Coins (Financial Sustainability)
        - 40% Eco-Mode Utilization (Operational Efficiency)
        - 20% Device Variety (Ecosystem Diversity)
        """
        for user in self:
            # 1. Happiness Coin Component (Max 40 pts)
            coin_score = min(40.0, user.happiness_coin_balance / 2.0)

            # 2. Eco-Mode Component (Max 40 pts)
            devices = self.env['pms.device'].search([('resident_id', '=', user.id)])
            total_devices = len(devices)
            eco_devices = len(devices.filtered(lambda d: d.eco_mode))
            eco_score = (eco_devices / total_devices * 40.0) if total_devices > 0 else 0.0

            # 3. Device Variety Component (Max 20 pts)
            unique_types = len(set(devices.mapped('device_type')))
            variety_score = min(20.0, unique_types * 4.0)

            user.eco_efficiency_score = int(min(100, coin_score + eco_score + variety_score))

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True
