from odoo import models, fields, api
import uuid

class VoucherTemplate(models.Model):
    _name = 'pms.voucher.template'
    _description = 'Voucher Template'

    name = fields.Char(string='Voucher Name', required=True)
    merchant_id = fields.Many2one('res.partner', string='Merchant')
    coin_cost = fields.Float(string='Cost (Happiness Coins)', default=0.0)
    description = fields.Text(string='Description')

class Voucher(models.Model):
    _name = 'pms.voucher'
    _description = 'Community Voucher'

    template_id = fields.Many2one('pms.voucher.template', string='Template', required=True)
    resident_id = fields.Many2one('res.users', string='Resident')
    qr_code = fields.Char(string='QR Code', readonly=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired')
    ], default='active')

    @api.model
    def create(self, vals):
        if not vals.get('qr_code'):
            vals['qr_code'] = str(uuid.uuid4())
        return super(Voucher, self).create(vals)

    def action_redeem(self):
        self.ensure_one()
        if self.state == 'active':
            self.state = 'used'
            return True
        return False
