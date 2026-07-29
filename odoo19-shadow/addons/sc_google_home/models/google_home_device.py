from odoo import models, fields, api

class GoogleHomeDevice(models.Model):
    _name = 'sc.google.home.device'
    _description = 'Smart Control Google Home Device'

    name = fields.Char(string='Device Name', required=True)
    device_type = fields.Char(string='Google Home Device Type', default='action.devices.types.LIGHT')
    traits = fields.Char(string='Traits (comma separated)', default='action.devices.traits.OnOff')

    state_on = fields.Boolean(string='Is On', default=False)
    brightness = fields.Integer(string='Brightness', default=100)

    def _get_google_home_state(self):
        self.ensure_one()
        state = {
            'online': True,
        }
        if 'action.devices.traits.OnOff' in self.traits:
            state['on'] = self.state_on
        if 'action.devices.traits.Brightness' in self.traits:
            state['brightness'] = self.brightness
        return state

    def _execute_google_home_command(self, command, params):
        self.ensure_one()
        if command == 'action.devices.commands.OnOff':
            self.state_on = params.get('on', False)
        elif command == 'action.devices.commands.BrightnessAbsolute':
            self.brightness = params.get('brightness', 100)
        return True
