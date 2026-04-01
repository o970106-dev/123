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
        """Compute eco-score based on device states and coin accumulation."""
        for user in self:
            devices = self.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
            score = 50.0 # Base score
            if devices:
                eco_count = len(devices.filtered(lambda d: d.eco_mode))
                off_count = len(devices.filtered(lambda d: not d.is_on and d.device_type == 'action.devices.types.LIGHT'))
                score += (eco_count / len(devices)) * 30
                score += (off_count / len(devices) if len(devices) > 0 else 0) * 20

            # Bonus for high coin balance
            if user.happiness_coin_balance > 100:
                score += 10

            user.eco_efficiency_score = min(100.0, score)

    def action_reward_sustainability(self, amount=5.0, reason="Energy Saving Mode"):
        """Grant Happiness Coins for sustainable behavior."""
        self.ensure_one()
        self.env['pms.happiness.coin'].create({
            'user_id': self.id,
            'amount': amount,
            'reason': reason
        })
        return True
