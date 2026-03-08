from odoo import models, fields

class PMSDevice(models.Model):
    _name = 'pms.device'
    _description = 'Shared PMS Smart Device'

    name = fields.Char(string='Device Name', required=True)
    device_type = fields.Selection([
        ('light', 'Light'),
        ('ac', 'Air Conditioner'),
        ('lock', 'Smart Lock'),
    ], string='Type', default='light')
    state = fields.Selection([
        ('on', 'ON'),
        ('off', 'OFF'),
    ], string='State', default='off')
    is_locked = fields.Boolean(string='Is Locked', default=True)
    resident_id = fields.Many2one('res.users', string='Resident Owner')
