from odoo import models, fields

class PMSDevice(models.Model):
    _name = 'pms.device'
    _description = 'Property Management Smart Device'

    name = fields.Char(string='Device Name', required=True)
    type = fields.Selection([
        ('light', 'Light'),
        ('ac', 'Air Conditioner'),
        ('lock', 'Smart Lock')
    ], string='Type', default='light')
    state = fields.Selection([
        ('on', 'On'),
        ('off', 'Off')
    ], string='State', default='off')
    resident_id = fields.Many2one('res.users', string='Resident')
    connectivity = fields.Boolean(string='Online', default=True)
