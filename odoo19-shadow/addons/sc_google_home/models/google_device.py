from odoo import models, fields

class GoogleHomeDevice(models.Model):
    _name = 'sc.google.home.device'
    _description = 'Google Home Device Mapping'

    name = fields.Char(string='Google Device Name', required=True)
    google_device_id = fields.Char(string='Google Device ID', required=True)
    resident_id = fields.Many2one('res.users', string='Resident')
    device_id = fields.Many2one('pms.device', string='Physical Device')
    device_type = fields.Selection(related='device_id.device_type', readonly=True)
