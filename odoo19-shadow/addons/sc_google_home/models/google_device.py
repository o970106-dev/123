from odoo import models, fields, api

class SCGoogleHomeDevice(models.Model):
    _name = 'sc.google.home.device'
    _description = 'Google Home Integrated Device'

    name = fields.Char(string='Name', required=True)
    google_device_id = fields.Char(string='Google Device ID', required=True)
    device_id = fields.Many2one('pms.device', string='Physical Device')

    device_type = fields.Selection([
        ('light', 'Light'),
        ('ac', 'AC'),
        ('lock', 'Lock'),
        ('sensor', 'Sensor'),
    ], string='Type', required=True)

    # Sensor state for Happiness Coins
    resident_id = fields.Many2one('res.users', string='Resident')
