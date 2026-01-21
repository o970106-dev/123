from odoo import models, fields

class SmartDevice(models.Model):
    _name = 'smart.device'
    _description = 'Smart Home Device'

    name = fields.Char(string='Device Name', required=True)
    device_id = fields.Char(string='External ID', required=True)
    device_type = fields.Selection([
        ('action.devices.types.LIGHT', 'Light'),
        ('action.devices.types.OUTLET', 'Outlet'),
        ('action.devices.types.SWITCH', 'Switch'),
        ('action.devices.types.THERMOSTAT', 'Thermostat'),
    ], string='Google Device Type', default='action.devices.types.LIGHT')

    state = fields.Boolean(string='Is On', default=False)
    brightness = fields.Integer(string='Brightness', default=0)

    # In a real scenario, this would link to an IoT Gateway or hardware
    room_id = fields.Char(string='Room/Location')
