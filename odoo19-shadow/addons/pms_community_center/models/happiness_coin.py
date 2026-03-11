from odoo import models, fields, api

class HappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Happiness Coin Economy'
    _order = 'create_date desc'

    resident_id = fields.Many2one('res.users', string='Resident', required=True)
    amount = fields.Integer(string='Amount', required=True)
    transaction_type = fields.Selection([
        ('sustainability', 'Sustainability Reward'),
        ('volunteer', 'Volunteering Reward'),
        ('spend', 'Redemption'),
    ], string='Type', required=True)
    note = fields.Char(string='Transaction Note')

class ResUsers(models.Model):
    _inherit = 'res.users'

    happiness_coin_balance = fields.Integer(
        string='Happiness Coins', compute='_compute_happiness_balance'
    )

    def _compute_happiness_balance(self):
        """Optimized balance computation using read_group to avoid O(N) search in loops."""
        results = self.env['pms.happiness.coin'].read_group(
            [('resident_id', 'in', self.ids)],
            ['resident_id', 'amount:sum'],
            ['resident_id']
        )
        mapped_data = {res['resident_id'][0]: res['amount'] for res in results}
        for user in self:
            user.happiness_coin_balance = mapped_data.get(user.id, 0)

    def action_reward_sustainability(self):
        self.env['pms.happiness.coin'].create({
            'resident_id': self.id, 'amount': 5, 'transaction_type': 'sustainability', 'note': 'Energy Saving Mode Activated',
        })

    def action_reward_volunteer(self):
        self.env['pms.happiness.coin'].create({
            'resident_id': self.id, 'amount': 10, 'transaction_type': 'volunteer', 'note': 'Volunteer Delivery Completed',
        })
