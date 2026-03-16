from odoo import models, fields, api
import logging
from odoo.addons.pms_base.models.staps_core import staps_timed

_logger = logging.getLogger(__name__)

class HappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Happiness Coin Balance'
    _order = 'create_date desc'

    resident_id = fields.Many2one('res.users', string='Resident', required=True)
    amount = fields.Integer(string='Amount', required=True)
    transaction_type = fields.Selection([
        ('reward', 'Reward'),
        ('spend', 'Spend'),
        ('transfer', 'Transfer')
    ], string='Type', default='reward')
    description = fields.Char(string='Description')

    @api.model
    @staps_timed(persist=True)
    def get_balance(self, user_id):
        """
        Returns the current Happiness Coin balance for a given user.
        Calculated as the sum of all transactions.
        """
        transactions = self.search([('resident_id', '=', user_id)])
        return sum(transactions.mapped('amount'))

    @api.model
    @staps_timed(persist=True)
    def add_reward(self, user_id, amount, reason):
        """
        Adds a reward transaction for a resident.
        """
        return self.create({
            'resident_id': user_id,
            'amount': amount,
            'transaction_type': 'reward',
            'description': reason
        })
