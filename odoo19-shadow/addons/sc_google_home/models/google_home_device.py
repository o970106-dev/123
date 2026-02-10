from odoo import models, fields, api
import logging
from odoo.addons.pms_base.models.staps_core import staps_timed

_logger = logging.getLogger(__name__)

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

    # New: Lock status
    is_locked = fields.Boolean(string='Is Locked', default=True)

    # Fan Speed support
    fan_speed = fields.Char(string='Fan Speed', default='medium')

    @staps_timed
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
        if 'action.devices.traits.LockUnlock' in trait_list:
            state['isLocked'] = self.is_locked
            state['isJammed'] = False
        if 'action.devices.traits.OccupancySensing' in trait_list:
            # Link to vt module (mock logic for now)
            state['occupancy'] = 'OCCUPIED' if self.state_on else 'UNOCCUPIED'
        if 'action.devices.traits.SensorState' in trait_list:
            # Happiness Coin Balance as a sensor
            balance = self.env['pms.happiness.coin'].get_balance(self.partner_id.id)
            state['sensorStateData'] = [{
                'name': 'Happiness Coins',
                'numericValue': balance,
                'feature': 'COMMUNITY_SCORE'
            }]

        return state

    @staps_timed
    def _execute_google_home_command(self, command, params):
        self.ensure_one()
        _logger.info("Executing Google Home command: %s with params %s", command, params)

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
        elif command == 'action.devices.commands.LockUnlock':
            self.is_locked = params.get('lock', True)
        elif command == 'action.devices.commands.ActivateScene':
            if self.device_type == 'action.devices.types.SCENE':
                _logger.info("CNS BROADCAST: Activating scene: %s", self.name)
                # In a real scenario, this would trigger multiple device actions via STAPS
        return True

    def action_energy_saving_mode(self):
        """
        Cross-module method to be called by Energy (er) module.
        Implements energy saving logic per device type.
        """
        self.ensure_one()
        _logger.info("STAPS TRIGGER: Energy saving mode for device: %s", self.name)
        if self.device_type == 'action.devices.types.LIGHT':
            self.brightness = 20 # Dim lights
        elif self.device_type == 'action.devices.types.THERMOSTAT':
            self.target_temp = 27.0 # Increase AC target temp
        return True
