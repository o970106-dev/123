from odoo import models, fields, api

class PMSHappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Happiness Coin'

    resident_id = fields.Many2one('res.users', string='Resident', required=True)
    balance = fields.Integer(string='Balance', default=0)
    transaction_ids = fields.One2many('pms.happiness.coin.history', 'coin_id', string='Transactions')

class PMSHappinessCoinHistory(models.Model):
    _name = 'pms.happiness.coin.history'
    _description = 'Happiness Coin Transaction History'

    coin_id = fields.Many2one('pms.happiness.coin', string='Coin Account')
    amount = fields.Integer(string='Amount')
    reason = fields.Char(string='Reason')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    happiness_coin_balance = fields.Integer(string='Happiness Coin Balance', compute='_compute_coin_balance')

    def _compute_coin_balance(self):
        for rec in self:
            user = rec.user_ids[:1]
            if user:
                coin = self.env['pms.happiness.coin'].search([('resident_id', '=', user.id)], limit=1)
                rec.happiness_coin_balance = coin.balance if coin else 0
            else:
                rec.happiness_coin_balance = 0

    def action_reward_sustainability(self):
        """Reward 5 coins for energy-saving behavior."""
        self._add_coins(5, 'Energy Saving Reward')

    def action_reward_volunteer(self):
        """Reward 10 coins for volunteer delivery."""
        self._add_coins(10, 'Volunteer Delivery Reward')

    def _add_coins(self, amount, reason):
        user = self.user_ids[:1]
        if not user: return
        coin = self.env['pms.happiness.coin'].search([('resident_id', '=', user.id)], limit=1)
        if not coin:
            coin = self.env['pms.happiness.coin'].create({'resident_id': user.id})

        self.env['pms.happiness.coin.history'].create({
            'coin_id': coin.id,
            'amount': amount,
            'reason': reason
        })
        coin.balance += amount
