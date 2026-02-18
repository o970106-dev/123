from odoo import models, fields, api

class PMSDevice(models.Model):
    _name = 'pms.device'
    _description = 'PMS Smart Device'

    name = fields.Char(string='Name', required=True)
    device_type = fields.Selection([
        ('light', 'Light'),
        ('ac', 'AC'),
        ('lock', 'Lock'),
    ], string='Type', default='light')
    is_on = fields.Boolean(string='Is On', default=False)
    connectivity_status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
    ], string='Status', default='online')

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Security Token', copy=False)
