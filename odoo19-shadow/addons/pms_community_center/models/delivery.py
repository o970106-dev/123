from odoo import models, fields, api

class VolunteerDelivery(models.Model):
    _name = 'pms.delivery.order'
    _description = 'Volunteer Delivery Order'

    name = fields.Char(string='Order Number', required=True, copy=False, readonly=True, default='New')
    volunteer_id = fields.Many2one('res.users', string='Volunteer')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('done', 'Completed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pms.delivery.order') or 'DEL' + str(fields.Datetime.now().timestamp())
        return super().create(vals)

    def action_complete_delivery(self):
        self.ensure_one()
        if self.state == 'done':
            return
        self.state = 'done'
        # Reward volunteer with 10 coins
        coin_record = self.env['pms.happiness.coin'].sudo().search([('resident_id', '=', self.volunteer_id.id)], limit=1)
        if not coin_record:
            coin_record = self.env['pms.happiness.coin'].sudo().create({'resident_id': self.volunteer_id.id})

        self.env['pms.happiness.coin.history'].sudo().create({
            'coin_id': coin_record.id,
            'amount': 10.0,
            'type': 'earn',
            'description': f'Reward for delivery {self.name}'
        })
