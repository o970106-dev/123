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
        """Compute Eco-Efficiency Score based on device states and coins."""
        for user in self:
            devices = self.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
            eco_devices = len(devices.filtered(lambda d: d.eco_mode))
            total_devices = len(devices) or 1
            # Base score from eco mode ratio + bonus from happiness coins
            device_score = (eco_devices / total_devices) * 100.0
            coin_bonus = min(user.happiness_coin_balance / 10.0, 50.0)
            user.eco_efficiency_score = min(device_score + coin_bonus, 100.0)

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True
