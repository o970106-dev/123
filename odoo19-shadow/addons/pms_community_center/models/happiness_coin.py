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

    happiness_coin_balance = fields.Float(string='Happiness Coin Balance', compute='_compute_coin_balance')
    is_volunteer = fields.Boolean(string='Is Volunteer', default=False)

    def _compute_coin_balance(self):
        for user in self:
            txs = self.env['pms.happiness.coin'].search([('resident_id', '=', user.id)])
            balance = sum(t.amount if t.transaction_type == 'earn' else -t.amount for t in txs)
            user.happiness_coin_balance = balance
