from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VoucherValidationWizard(models.TransientModel):
    _name = 'pms.voucher.validation.wizard'
    _description = 'Voucher Validation Wizard'

    qr_code = fields.Char(string='Scan QR Code', required=True)

    def action_validate(self):
        voucher = self.env['pms.voucher'].search([('qr_code', '=', self.qr_code), ('state', '=', 'active')], limit=1)
        if not voucher:
            raise UserError(_("Invalid or already used voucher!"))
        voucher.action_redeem()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Voucher %s validated successfully.') % voucher.template_id.name,
                'sticky': False,
            }
        }
