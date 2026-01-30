from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    google_home_token = fields.Char(string='Google Home Sync Token', groups='base.group_system')

class GoogleHomeDevice(models.Model):
    _name = 'sc.google.home.device'
    _description = 'Smart Control Google Home Device'

    name = fields.Char(string='Device Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Owner (Resident)')
    room_name = fields.Char(string='Room Name', help="Used for roomHint in Google Home")
    device_type = fields.Char(string='Google Home Device Type', default='action.devices.types.LIGHT')
    traits = fields.Char(string='Traits (comma separated)', default='action.devices.traits.OnOff',
                         help="e.g. action.devices.traits.OnOff,action.devices.traits.Brightness")

    state_on = fields.Boolean(string='Is On', default=False)
    brightness = fields.Integer(string='Brightness', default=100)
    color_temp = fields.Integer(string='Color Temperature (K)', default=3000)
    target_temp = fields.Float(string='Target Temperature', default=25.0)

    # Advanced Traits Support
    fan_speed = fields.Char(string='Fan Speed', default='medium')
    current_temp = fields.Float(string='Current Temperature', default=24.5)
    hvac_mode = fields.Selection([
        ('off', 'Off'),
        ('heat', 'Heat'),
        ('cool', 'Cool'),
        ('auto', 'Auto')
    ], string='HVAC Mode', default='cool')

    # Optimization: Sync Status
    last_sync_timestamp = fields.Datetime(string='Last Cloud Sync', default=fields.Datetime.now)

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
            state['thermostatTemperatureAmbient'] = self.current_temp
            state['thermostatTemperatureSetpoint'] = self.target_temp
            state['thermostatMode'] = self.hvac_mode
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
        elif command == 'action.devices.commands.ThermostatSetMode':
            self.hvac_mode = params.get('thermostatMode')
        elif command == 'action.devices.commands.SetFanSpeed':
            self.fan_speed = params.get('fanSpeed')
        elif command == 'action.devices.commands.ActivateScene':
            if self.device_type == 'action.devices.types.SCENE':
                _logger.info("Activating scene: %s", self.name)

        self.last_sync_timestamp = fields.Datetime.now()
        return True

    def action_energy_saving_mode(self):
        """
        Highest degree optimization: Property-wide energy saving protocol.
        Triggered via STAPS broadcast from CNS.
        """
        self.ensure_one()
        _logger.info("[STAPS] Triggering energy saving mode for device: %s", self.name)

        if self.device_type == 'action.devices.types.LIGHT':
            self.brightness = 20 # Dim to 20%
            self.state_on = True # Keep on but dim
        elif self.device_type == 'action.devices.types.THERMOSTAT':
            self.target_temp = 27.0 # Eco temperature

        self.last_sync_timestamp = fields.Datetime.now()
        return True
