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
    temperature = fields.Float(string='Current Temperature', default=25.0)
    target_temperature = fields.Float(string='Target Temperature', default=25.0)
    fan_speed = fields.Integer(string='Fan Speed', default=0)
    color_temp = fields.Integer(string='Color Temperature', default=3000)
    brightness = fields.Integer(string='Brightness', default=100)
    room_name = fields.Char(string='Room Name', default='Living Room')
    eco_mode = fields.Boolean(string='Eco Mode', default=False)

    resident_id = fields.Many2one('res.users', string='Resident')

    @api.depends('name')
    def _compute_google_id(self):
        for rec in self:
            rec.google_device_id = f"pms_dev_{rec.id}"

    def get_google_traits(self):
        """Centralized trait mapping for Google Home."""
        if self.device_type == 'action.devices.types.SCENE':
            return ['action.devices.traits.Scene']

        traits = ['action.devices.traits.OnOff']
        if self.device_type == 'action.devices.types.LOCK':
            traits.append('action.devices.traits.LockUnlock')
        elif self.device_type == 'action.devices.types.THERMOSTAT':
            traits.append('action.devices.traits.TemperatureSetting')

        if self.device_type == 'action.devices.types.LIGHT':
            traits.append('action.devices.traits.Brightness')
            traits.append('action.devices.traits.ColorTemperature')

        traits.append('action.devices.traits.FanSpeed')
        return traits

    def get_google_attributes(self):
        """Centralized attribute mapping for Google Home."""
        attrs = {}
        if self.device_type == 'action.devices.types.SCENE':
            attrs['sceneReversible'] = True
            return attrs

        if 'action.devices.traits.TemperatureSetting' in self.get_google_traits():
            attrs.update({
                'thermostatTemperatureUnit': 'C',
                'availableThermostatModes': ['off', 'heat', 'cool', 'on'],
            })

        if 'action.devices.traits.Brightness' in self.get_google_traits():
            attrs['commandOnlyBrightness'] = False

        if 'action.devices.traits.ColorTemperature' in self.get_google_traits():
            attrs['colorTemperatureRange'] = {
                'temperatureMinK': 2000,
                'temperatureMaxK': 9000
            }

        if 'action.devices.traits.FanSpeed' in self.get_google_traits():
            attrs['availableFanSpeeds'] = {
                'speeds': [
                    {'speed_name': 'Low', 'speed_values': [{'speed_synonym': ['low', 'slow'], 'lang': 'en'}]},
                    {'speed_name': 'High', 'speed_values': [{'speed_synonym': ['high', 'fast'], 'lang': 'en'}]}
                ],
                'ordered': True
            }

        return attrs

class PmsTelemetry(models.Model):
    _name = 'pms.telemetry'
    _description = 'PMS STAPS Telemetry'
    _order = 'timestamp desc'

    name = fields.Char(string='Action Name')
    duration = fields.Float(string='Duration (ms)')
    coordinate = fields.Char(string='STAPS Coordinate')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    source_node = fields.Char(string='Source Node', default='CNS-Main')
    error = fields.Text(string='Error Detail')
