from odoo import models, fields, api

class PMSDevice(models.Model):
    _name = 'pms.device'
    _description = 'PMS Smart Device'

    name = fields.Char(string='Name', required=True)
    device_type = fields.Selection([
        ('light', 'Light'),
        ('ac', 'AC'),
        ('lock', 'Lock'),
        ('fan', 'Fan'),
        ('thermostat', 'Thermostat'),
    ], string='Type', default='light')
    is_on = fields.Boolean(string='Is On', default=False)
    state_json = fields.Text(string='Advanced State (JSON)')
    connectivity_status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
    ], string='Status', default='online')
    last_update = fields.Datetime(string='Last Update', default=fields.Datetime.now)

class PMSTelemetry(models.Model):
    _name = 'pms.telemetry'
    _description = 'PMS STAPS Telemetry'
    _order = 'create_date desc'

    node_id = fields.Char(string='Node ID')
    operation = fields.Char(string='Operation')
    coordinate = fields.Char(string='STAPS Coordinate')
    duration = fields.Float(string='Duration (ms)')
    effective_duration = fields.Float(string='Effective Duration (ms)')

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Security Token', copy=False)
    happiness_coin_balance = fields.Float(related='partner_id.happiness_coin_balance', readonly=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    happiness_coin_balance = fields.Float(string='Happiness Coin Balance', default=0.0)
