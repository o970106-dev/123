from odoo import models, fields

class PmsDevice(models.Model):
    _name = 'pms.device'
    _description = 'Smart Device'

    name = fields.Char(string='Device Name', required=True)
    type = fields.Selection([
        ('light', 'Light'),
        ('ac', 'Air Conditioner'),
        ('lock', 'Smart Lock')
    ], string='Type', default='light')
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline')
    ], string='Connectivity', default='online')
    state = fields.Boolean(string='Is On', default=False)
    resident_id = fields.Many2one('res.users', string='Resident')
