from odoo import models, fields, api
from odoo.addons.pms_base.models.staps_core import staps_timed

class HappinessCoin(models.Model):
    _name = 'pms.happiness.coin'
    _description = 'Happiness Coin Transaction'
    _order = 'create_date desc'

    resident_id = fields.Many2one('res.users', string='Resident', required=True)
    amount = fields.Float(string='Amount', required=True)
    description = fields.Char(string='Description')
    transaction_type = fields.Selection([
        ('reward', 'Reward'),
        ('spend', 'Spend'),
        ('transfer', 'Transfer'),
    ], string='Type', default='reward')

    @api.model
    @staps_timed
    def action_reward_delivery(self, user_id):
        """Reward a resident for a community delivery."""
        return self.create({
            'resident_id': user_id,
            'amount': 10.0,
            'description': 'Volunteer Delivery Reward',
            'transaction_type': 'reward',
        })

    @api.model
    @staps_timed
    def action_reward_sustainability(self, user_id):
        """Reward a resident for energy saving behaviors."""
        return self.create({
            'resident_id': user_id,
            'amount': 5.0,
            'description': 'Energy Saving Sustainability Reward',
            'transaction_type': 'reward',
        })

    @api.model
    def create(self, vals):
        res = super(HappinessCoin, self).create(vals)
        # Update user balance
        user = self.env['res.users'].browse(vals['resident_id'])
        user.partner_id.happiness_coin_balance += vals['amount']
        return res

class PMSDeviceCC(models.Model):
    _inherit = 'pms.device'

    @staps_timed
    def action_energy_saving_mode(self):
        """Optimize device for energy saving and reward user."""
        for record in self:
            if record.device_type in ['ac', 'light']:
                record.write({'is_on': False})
                # Mock rewarding current user
                self.env['pms.happiness.coin'].action_reward_sustainability(self.env.uid)
