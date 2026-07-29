from odoo import models, fields, api

class GoogleHomeDevice(models.Model):
    _name = 'sc.google.home.device'
    _description = 'Smart Control Google Home Device'

    name = fields.Char(string='Device Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Owner (Resident)')
    device_type = fields.Char(string='Google Home Device Type', default='action.devices.types.LIGHT')
    traits = fields.Char(string='Traits (comma separated)', default='action.devices.traits.OnOff',
                         help="e.g. action.devices.traits.OnOff,action.devices.traits.Brightness")

    state_on = fields.Boolean(string='Is On', default=False)
    brightness = fields.Integer(string='Brightness', default=100)
    color_temp = fields.Integer(string='Color Temperature (K)', default=3000)
    target_temp = fields.Float(string='Target Temperature', default=25.0)

    # Fan Speed support
    fan_speed = fields.Char(string='Fan Speed', default='medium')

    def _get_google_home_state(self):
        self.ensure_one()
        state = {
            'online': True,
        }
        trait_list = self.traits.split(',')
        if 'action.devices.traits.OnOff' in trait_list:
            state['on'] = self.state_on
        if 'action.devices.traits.Brightness' in trait_list:
            state['brightness'] = self.brightness
        if 'action.devices.traits.ColorSetting' in trait_list:
            state['color'] = {
                'temperatureK': self.color_temp
            }
        if 'action.devices.traits.TemperatureSetting' in trait_list:
            state['thermostatTemperatureAmbient'] = 24.5 # Mock sensor data
            state['thermostatTemperatureSetpoint'] = self.target_temp
            state['thermostatMode'] = 'cool'
        if 'action.devices.traits.FanSpeed' in trait_list:
            state['currentFanSpeedSetting'] = self.fan_speed
        return state

    def _execute_google_home_command(self, command, params):
        self.ensure_one()
        if command == 'action.devices.commands.OnOff':
            self.state_on = params.get('on', False)
        elif command == 'action.devices.commands.BrightnessAbsolute':
            self.brightness = params.get('brightness', 100)
        elif command == 'action.devices.commands.ColorAbsolute':
            if 'temperature' in params:
                self.color_temp = params.get('temperature')
        elif command == 'action.devices.commands.ThermostatTemperatureSetpoint':
            self.target_temp = params.get('thermostatTemperatureSetpoint')
        elif command == 'action.devices.commands.SetFanSpeed':
            self.fan_speed = params.get('fanSpeed')
        return True
