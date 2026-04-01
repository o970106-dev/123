from odoo import models, fields, api

class PmsDevice(models.Model):
    _name = 'pms.device'
    _description = 'PMS Smart Device'

    name = fields.Char(string='Device Name', required=True)
    google_device_id = fields.Char(string='Google Device ID', compute='_compute_google_id', store=True)
    device_type = fields.Selection([
        ('action.devices.types.LIGHT', 'Light'),
        ('action.devices.types.OUTLET', 'Outlet'),
        ('action.devices.types.THERMOSTAT', 'Thermostat'),
        ('action.devices.types.LOCK', 'Lock'),
        ('action.devices.types.SCENE', 'Scene'),
    ], string='Type', default='action.devices.types.LIGHT')

    is_on = fields.Boolean(string='Is On', default=False)
    is_locked = fields.Boolean(string='Is Locked', default=True)
    brightness = fields.Integer(string='Brightness', default=100)
    temperature = fields.Float(string='Current Temperature', default=25.0)
    target_temperature = fields.Float(string='Target Temperature', default=25.0)
    fan_speed = fields.Integer(string='Fan Speed', default=0)
    color_temp = fields.Integer(string='Color Temperature', default=3000)
    eco_mode = fields.Boolean(string='Eco Mode', default=False)
    room_name = fields.Char(string='Room Name', default='Living Room')

    resident_id = fields.Many2one('res.users', string='Resident')

    @api.depends('name')
    def _compute_google_id(self):
        for rec in self:
            rec.google_device_id = f"pms_dev_{rec.id}"

class PmsTelemetry(models.Model):
    _name = 'pms.telemetry'
    _description = 'PMS STAPS Telemetry'
    _order = 'timestamp desc'

    name = fields.Char(string='Action Name')
    duration = fields.Float(string='Duration (ms)')
    coordinate = fields.Char(string='STAPS Coordinate')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    source_node = fields.Char(string='Source Node', default='CNS-Main')
