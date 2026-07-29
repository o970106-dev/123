from odoo import models, fields, api

class HappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Community Happiness Coin Transaction'

    resident_id = fields.Many2one('res.users', string='Resident', required=True)
    amount = fields.Float(string='Amount', required=True)
    transaction_type = fields.Selection([
        ('earn', 'Earned'),
        ('spend', 'Spent')
    ], string='Type', required=True)
    description = fields.Char(string='Description')

class ResUsers(models.Model):
    _inherit = 'res.users'

    happiness_coin_balance = fields.Float(string='Happiness Coin Balance', compute='_compute_coin_balance', store=False)
    is_volunteer = fields.Boolean(string='Is Volunteer', default=False)

    def _compute_coin_balance(self):
        # Optimization: Use read_group to avoid search-in-loop performance hit
        domain = [('resident_id', 'in', self.ids)]
        tx_data = self.env['pms.happiness.coin'].read_group(
            domain, ['resident_id', 'amount', 'transaction_type'], ['resident_id', 'transaction_type'], lazy=False
        )

        balances = {uid: 0.0 for uid in self.ids}
        for data in tx_data:
            uid = data['resident_id'][0]
            amount = data['amount']
            if data['transaction_type'] == 'earn':
                balances[uid] += amount
            else:
                balances[uid] -= amount

        for user in self:
            user.happiness_coin_balance = balances.get(user.id, 0.0)
