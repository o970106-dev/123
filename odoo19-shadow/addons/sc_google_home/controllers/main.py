from odoo import http
from odoo.http import request
import json
import logging
from odoo.addons.pms_base.models.staps_core import staps_timed

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    def _validate_auth(self):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            _logger.warning("Missing or invalid Authorization header")
            return False

        token = auth_header.split(' ')[1]
        expected_token = request.env['ir.config_parameter'].sudo().get_param('sc_google_home.bearer_token')

        if not expected_token:
            _logger.error("Google Home Bearer Token is not configured. Access denied.")
            return False

        return token == expected_token

    @http.route('/google_home/fulfillment', type='json', auth='public', methods=['POST'], csrf=False)
    @staps_timed
    def fulfillment(self, **kwargs):
        if not self._validate_auth():
            req_data = request.dispatcher.jsonrequest if hasattr(request, 'dispatcher') else {}
            return {'requestId': req_data.get('requestId'), 'payload': {'errorCode': 'authFailure'}}

        payload = request.dispatcher.jsonrequest
        inputs = payload.get('inputs', [{}])
        intent = inputs[0].get('intent')
        request_id = payload.get('requestId')

        _logger.info("STAPS CNS RECEIVED: Google Home Intent: %s", intent)

        if intent == 'action.devices.SYNC':
            return self._handle_sync(request_id)
        elif intent == 'action.devices.QUERY':
            return self._handle_query(request_id, inputs[0].get('payload'))
        elif intent == 'action.devices.EXECUTE':
            return self._handle_execute(request_id, inputs[0].get('payload'))

        return {'requestId': request_id, 'payload': {'errorCode': 'protocolError'}}

    def _handle_sync(self, request_id):
        agent_user_id = request.env['ir.config_parameter'].sudo().get_param('database.uuid') or 'pms-double-j'

        domain = []
        if not request.env.user.has_group('sc_google_home.group_smart_control_manager'):
            domain = [('partner_id', '=', request.env.user.partner_id.id)]

        devices = request.env['sc.google.home.device'].sudo().search(domain)
        device_list = []
        for dev in devices:
            dev_info = {
                'id': str(dev.id),
                'type': dev.device_type,
                'traits': dev.traits.split(','),
                'name': {'name': dev.name},
                'willReportState': True,
                'deviceInfo': {
                    'manufacturer': 'Double J PMS',
                    'model': 'STAPS-Edge-v1',
                    'hwVersion': '1.0.0',
                    'swVersion': '2.5.0'
                },
                'attributes': {}
            }

            trait_list = dev.traits.split(',')
            if 'action.devices.traits.FanSpeed' in trait_list:
                dev_info['attributes']['availableFanSpeeds'] = {
                    'speeds': [
                        {'speed_name': 'low', 'speed_values': [{'speed_synonym': ['low', 'slow'], 'lang': 'en'}]},
                        {'speed_name': 'medium', 'speed_values': [{'speed_synonym': ['medium', 'normal'], 'lang': 'en'}]},
                        {'speed_name': 'high', 'speed_values': [{'speed_synonym': ['high', 'fast'], 'lang': 'en'}]}
                    ],
                    'ordered': True
                }
            if 'action.devices.traits.TemperatureSetting' in trait_list:
                dev_info['attributes']['thermostatTemperatureUnit'] = 'C'
                dev_info['attributes']['availableThermostatModes'] = 'off,heat,cool,on'

            if dev.room_name:
                dev_info['roomHint'] = dev.room_name
            device_list.append(dev_info)

        return {
            'requestId': request_id,
            'payload': {
                'agentUserId': agent_user_id,
                'devices': device_list
            }
        }

    def _handle_query(self, request_id, payload):
        device_ids = [d['id'] for d in payload.get('devices', [])]
        domain = [('id', 'in', [int(did) for did in device_ids if did.isdigit()])]

        devices = request.env['sc.google.home.device'].sudo().search(domain)
        dev_states = {str(dev.id): dev._get_google_home_state() for dev in devices}

        return {'requestId': request_id, 'payload': {'devices': dev_states}}

    def _handle_execute(self, request_id, payload):
        commands = payload.get('commands', [])
        results = []
        for command in commands:
            device_ids = [d['id'] for d in command.get('devices', [])]
            for execution in command.get('execution', []):
                action = execution.get('command')
                params = execution.get('params')

                domain = [('id', 'in', [int(did) for did in device_ids if did.isdigit()])]
                devices = request.env['sc.google.home.device'].sudo().search(domain)

                executed_ids = []
                for dev in devices:
                    dev._execute_google_home_command(action, params)
                    executed_ids.append(str(dev.id))

                if executed_ids:
                    results.append({
                        'ids': executed_ids,
                        'status': 'SUCCESS',
                        'states': devices[0]._get_google_home_state() if len(devices) == 1 else {'online': True}
                    })
        return {'requestId': request_id, 'payload': {'commands': results}}
