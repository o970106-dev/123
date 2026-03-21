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
    ], string='Type', default='action.devices.types.LIGHT')

    is_on = fields.Boolean(string='Is On', default=False)
    is_locked = fields.Boolean(string='Is Locked', default=True)
    temperature = fields.Float(string='Current Temperature', default=25.0)
    target_temperature = fields.Float(string='Target Temperature', default=25.0)
    fan_speed = fields.Integer(string='Fan Speed', default=0)
    color_temp = fields.Integer(string='Color Temperature', default=3000)
    brightness = fields.Integer(string='Brightness', default=100)
    room_name = fields.Char(string='Room Name', default='Living Room')

    resident_id = fields.Many2one('res.users', string='Resident')

    def get_google_traits(self):
        """Return a list of Google Home traits for this device."""
        traits = ['action.devices.traits.OnOff']
        if self.device_type == 'action.devices.types.LOCK':
            traits.append('action.devices.traits.LockUnlock')
        elif self.device_type == 'action.devices.types.THERMOSTAT':
            traits.append('action.devices.traits.TemperatureSetting')
        elif self.device_type == 'action.devices.types.LIGHT':
            traits.append('action.devices.traits.Brightness')
            traits.append('action.devices.traits.ColorTemperature')

        # Universal optimization traits for PMS
        traits.append('action.devices.traits.FanSpeed')
        traits.append('action.devices.traits.SensorState')
        traits.append('action.devices.traits.Scene')
        return list(set(traits))

    def get_google_attributes(self):
        """Return Google Home attributes for this device."""
        attrs = {
            'sensorStates': [
                {
                    'name': 'Happiness Coins',
                    'numericCapabilities': {'unit': 'COIN'},
                    'feature': 'COMMUNITY_SCORE'
                }
            ],
            'availableFanSpeeds': {
                'speeds': [
                    {'speed_name': 'Low', 'speed_values': [{'speed_synonym': ['low', 'slow'], 'lang': 'en'}]},
                    {'speed_name': 'High', 'speed_values': [{'speed_synonym': ['high', 'fast'], 'lang': 'en'}]}
                ],
                'ordered': True
            }
        }
        if self.device_type == 'action.devices.types.THERMOSTAT':
            attrs.update({
                'availableThermostatModes': ['off', 'heat', 'cool', 'on'],
                'thermostatTemperatureUnit': 'C'
            })

        traits = self.get_google_traits()
        if 'action.devices.traits.ColorTemperature' in traits:
            attrs['colorTemperatureRange'] = {
                'temperatureMinK': 2000,
                'temperatureMaxK': 9000
            }
        return attrs

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
