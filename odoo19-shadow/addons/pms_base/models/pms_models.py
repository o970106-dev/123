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

class PMSTelemetry(models.Model):
    _name = 'pms.telemetry'
    _description = 'PMS High-Precision Telemetry'
    _order = 'timestamp desc'

    action_name = fields.Char(string='Action Name', required=True)
    duration_ms = fields.Float(string='Duration (ms)', digits=(16, 4))
    staps_coordinate = fields.Char(string='STAPS Coordinate')
    source_node = fields.Selection([
        ('pm', 'PM'), ('pf', 'PF'), ('vt', 'VT'), ('cc', 'CC'),
        ('sc', 'SC'), ('er', 'ER'), ('ax1', 'AX1'), ('ax2', 'AX2')
    ], string='Source Node', default='pm')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Security Token', copy=False)
