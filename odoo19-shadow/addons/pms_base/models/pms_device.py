from odoo import models, fields, api

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
    temperature = fields.Float(string='Current Temperature', default=25.0)
    target_temperature = fields.Float(string='Target Temperature', default=25.0)
    resident_id = fields.Many2one('res.users', string='Resident Owner')
    google_device_id = fields.Char(string='Google Device ID', compute='_compute_google_id', store=True)

    @api.depends('id')
    def _compute_google_id(self):
        for dev in self:
            dev.google_device_id = f"pms_dev_{dev.id}"

    def get_google_traits(self):
        traits = ['action.devices.traits.OnOff']
        if self.device_type == 'lock':
            traits.append('action.devices.traits.LockUnlock')
        if self.device_type == 'ac':
            traits.append('action.devices.traits.TemperatureSetting')
        traits.append('action.devices.traits.SensorState')
        return traits

    def get_google_capabilities(self):
        caps = {
            'action.devices.traits.SensorState': {
                'numericCapabilities': [
                    {'name': 'Happiness Coins', 'unit': 'COIN'}
                ]
            }
        }
        if self.device_type == 'ac':
            caps.update({
                'thermostatTemperatureUnit': 'C',
                'thermostatTemperatureRange': {
                    'minThresholdCelsius': 16.0,
                    'maxThresholdCelsius': 30.0
                }
            })
        if self.device_type == 'lock':
            caps.update({
                'lockUnlockRetracting': True
            })
        return caps
