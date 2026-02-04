from odoo import models, fields, api, exceptions

class HappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Happiness Coin'

    resident_id = fields.Many2one('res.users', string='Resident', required=True, index=True)
    balance = fields.Float(string='Balance', default=0.0, readonly=True)
    transaction_ids = fields.One2many('pms.happiness.coin.history', 'coin_id', string='Transactions')

    _sql_constraints = [
        ('resident_unique', 'unique(resident_id)', 'A resident can only have one coin account!')
    ]

class HappinessCoinHistory(models.Model):
    _name = 'pms.happiness.coin.history'
    _description = 'Happiness Coin History'
    _order = 'date desc'

    coin_id = fields.Many2one('pms.happiness.coin', string='Coin Account', required=True, ondelete='cascade')
    amount = fields.Float(string='Amount', required=True)
    type = fields.Selection([('earn', 'Earned'), ('spend', 'Spent')], string='Type', required=True)
    description = fields.Char(string='Description')
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            coin = self.env['pms.happiness.coin'].browse(vals['coin_id'])
            new_balance = coin.balance + (vals['amount'] if vals['type'] == 'earn' else -vals['amount'])
            if new_balance < 0:
                raise exceptions.UserError("Insufficient Happiness Coins!")
            # Update parent balance
            coin.sudo().write({'balance': new_balance})
        return super().create(vals_list)

    def write(self, vals):
        raise exceptions.UserError("Transaction history cannot be modified!")

    def unlink(self):
        raise exceptions.UserError("Transaction history cannot be deleted!")
