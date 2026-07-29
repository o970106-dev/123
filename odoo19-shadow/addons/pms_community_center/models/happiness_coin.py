from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    happiness_coin_balance = fields.Integer(string='Happiness Coin Balance', default=0)

class HappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Happiness Coin Transaction'

    resident_id = fields.Many2one('res.users', string='Resident', required=True)
    amount = fields.Integer(string='Amount', required=True)
    type = fields.Selection([
        ('earn', 'Earned'),
        ('spend', 'Spent')
    ], string='Type', required=True)
    reason = fields.Char(string='Reason')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        res = super(HappinessCoin, self).create(vals)
        # Update resident balance
        resident = res.resident_id
        if res.type == 'earn':
            resident.happiness_coin_balance += res.amount
        else:
            resident.happiness_coin_balance -= res.amount
        return res
