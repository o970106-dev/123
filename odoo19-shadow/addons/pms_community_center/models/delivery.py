from odoo import models, fields, api

class DeliveryOrder(models.Model):
    _name = 'pms.delivery.order'
    _description = 'Volunteer Delivery Order'

    name = fields.Char(string='Order Reference', required=True)
    resident_id = fields.Many2one('res.users', string='Customer')
    volunteer_id = fields.Many2one('res.users', string='Volunteer', domain=[('is_volunteer', '=', True)])
    pickup_address = fields.Char(string='Pickup Address')
    delivery_address = fields.Char(string='Delivery Address')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Waiting for Volunteer'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default='draft')

    def action_assign_volunteer(self, volunteer_id):
        self.write({
            'volunteer_id': volunteer_id,
            'state': 'assigned'
        })

    def action_done(self):
        self.ensure_one()
        if self.state != 'delivered':
            self.state = 'delivered'
            # Award 10 Happiness Coins to the volunteer
            if self.volunteer_id:
                self.env['pms.happiness.coin'].create({
                    'resident_id': self.volunteer_id.id,
                    'amount': 10.0,
                    'transaction_type': 'earn',
                    'description': f'Reward for delivery {self.name}'
                })
        return True
