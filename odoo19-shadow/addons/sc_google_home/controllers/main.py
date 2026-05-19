from odoo import http
from odoo.http import request
import json
import logging
from contextlib import contextmanager

try:
    from odoo.addons.pms_base.models.staps_core import timed_process
except ImportError:
    @contextmanager
    def timed_process(name):
        yield

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):
    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kw):
        with timed_process("Google Home Fulfillment CNS Broadcast"):
            # Verification of token
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return request.make_response(json.dumps({'status': 'error', 'message': 'Unauthorized'}), [('Content-Type', 'application/json')], status=401)

            token = auth_header.split(' ')[1]
            user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)
            if not user:
                return request.make_response(json.dumps({'status': 'error', 'message': 'Invalid token'}), [('Content-Type', 'application/json')], status=403)

            # Manual body parsing for flat JSON
            data = json.loads(request.httprequest.data)
            inputs = data.get('inputs', [])

            results = []
            for input_data in inputs:
                intent = input_data.get('intent')
                if intent == 'action.devices.SYNC':
                    results.append(self._handle_sync(user))
                elif intent == 'action.devices.QUERY':
                    results.append(self._handle_query(user, input_data))
                elif intent == 'action.devices.EXECUTE':
                    results.append(self._handle_execute(user, input_data))

            response_data = {
                'requestId': data.get('requestId'),
                'payload': results[0] if results else {}
            }
            return request.make_response(json.dumps(response_data), [('Content-Type', 'application/json')])

    def _handle_sync(self, user):
        devices = request.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
        device_list = []
        for dev in devices:
            device_list.append({
                'id': str(dev.id),
                'type': self._map_device_type(dev.type),
                'traits': self._get_traits(dev.type),
                'name': {'name': dev.name},
                'willReportState': True,
                'attributes': self._get_attributes(dev.type)
            })
        return {'agentUserId': str(user.id), 'devices': device_list}

    def _map_device_type(self, dev_type):
        mapping = {
            'light': 'action.devices.types.LIGHT',
            'ac': 'action.devices.types.AC_UNIT',
            'lock': 'action.devices.types.LOCK',
        }
        return mapping.get(dev_type, 'action.devices.types.LIGHT')

    def _get_traits(self, dev_type):
        traits = ['action.devices.traits.OnOff']
        if dev_type == 'ac':
            traits.extend([
                'action.devices.traits.TemperatureSetting',
                'action.devices.traits.FanSpeed'
            ])
        elif dev_type == 'light':
            traits.append('action.devices.traits.ColorSetting')
        return traits

    def _get_attributes(self, dev_type):
        if dev_type == 'ac':
            return {
                'availableFanSpeeds': {
                    'speeds': [
                        {'speed_name': 'low', 'speed_values': [{'speed_synonym': ['low', 'slow'], 'lang': 'en'}]},
                        {'speed_name': 'high', 'speed_values': [{'speed_synonym': ['high', 'fast'], 'lang': 'en'}]}
                    ],
                    'ordered': True
                },
                'thermostatTemperatureUnit': 'C'
            }
        elif dev_type == 'light':
            return {'colorTemperatureRange': {'temperatureMinK': 2000, 'temperatureMaxK': 9000}}
        return {}

    def _handle_query(self, user, input_data):
        payload_devices = {}
        devices_to_query = input_data.get('payload', {}).get('devices', [])
        for dev_in in devices_to_query:
            dev_id = dev_in.get('id')
            dev = request.env['pms.device'].sudo().browse(int(dev_id))
            payload_devices[dev_id] = {
                'online': dev.connectivity,
                'on': dev.state == 'on'
            }
        return {'devices': payload_devices}

    def _handle_execute(self, user, input_data):
        commands = input_data.get('payload', {}).get('commands', [])
        results = []
        for command in commands:
            devices = command.get('devices', [])
            executions = command.get('execution', [])
            for dev_in in devices:
                dev_id = dev_in.get('id')
                dev = request.env['pms.device'].sudo().browse(int(dev_id))
                for execution in executions:
                    action = execution.get('command')
                    params = execution.get('params', {})
                    if action == 'action.devices.commands.OnOff':
                        dev.write({'state': 'on' if params.get('on') else 'off'})
                    elif action == 'action.devices.commands.ThermostatTemperatureSetpoint':
                        # Mock temperature update
                        _logger.info(f"Setting temperature for {dev.name} to {params.get('thermostatTemperatureSetpoint')}")
                    elif action == 'action.devices.commands.SetFanSpeed':
                        _logger.info(f"Setting fan speed for {dev.name} to {params.get('fanSpeed')}")

                    results.append({
                        'ids': [dev_id],
                        'status': 'SUCCESS',
                        'states': {'on': dev.state == 'on', 'online': True}
                    })
        return {'commands': results}
