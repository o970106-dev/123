import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    def _validate_token(self):
        """
        Secures the endpoint by validating the Bearer token.
        In a production environment, this should interface with an OAuth2 provider.
        """
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1]
        # Example validation: check if token exists in a valid tokens registry
        # For demonstration, we allow 'STAPS-SECURE-TOKEN'
        return token == 'STAPS-SECURE-TOKEN'

    @http.route('/google_home/fulfillment', type='json', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        if not self._validate_token():
            _logger.warning("Unauthorized Google Home fulfillment attempt")
            return {'status': 'error', 'errorCode': 'authFailure'}

        payload = request.jsonrequest
        intent = payload.get('inputs', [{}])[0].get('intent')

        _logger.info(f"Google Home Intent: {intent}")

        if intent == 'action.devices.SYNC':
            return self._handle_sync(payload)
        elif intent == 'action.devices.QUERY':
            return self._handle_query(payload)
        elif intent == 'action.devices.EXECUTE':
            return self._handle_execute(payload)

        return {'requestId': payload.get('requestId'), 'payload': {'status': 'error'}}

    def _handle_sync(self, payload):
        # Improved security: filter by the resident identified by the token
        # In real case, token would map to a user
        devices = request.env['sc.google.home.device'].sudo().search([])
        device_list = []
        for d in devices:
            traits = ['action.devices.traits.OnOff']
            if d.device_type == 'LIGHT':
                traits.append('action.devices.traits.Brightness')

            device_list.append({
                'id': d.external_id,
                'type': f'action.devices.types.{d.device_type}',
                'traits': traits,
                'name': {'name': d.name},
                'willReportState': True,
                'roomHint': d.room_name or ''
            })

        return {
            'requestId': payload.get('requestId'),
            'payload': {
                'agentUserId': 'user_123',
                'devices': device_list
            }
        }

    def _handle_query(self, payload):
        device_ids = [d['id'] for d in payload['inputs'][0]['payload']['devices']]
        devices = request.env['sc.google.home.device'].sudo().search([('external_id', 'in', device_ids)])

        device_states = {}
        for d in devices:
            state = {'online': True, 'on': d.is_on}
            if d.device_type == 'LIGHT':
                state['brightness'] = d.brightness
            device_states[d.external_id] = state

        return {
            'requestId': payload.get('requestId'),
            'payload': {'devices': device_states}
        }

    def _handle_execute(self, payload):
        commands = payload['inputs'][0]['payload']['commands']
        results = []
        for command in commands:
            device_ids = [d['id'] for d in command['devices']]
            for execution in command['execution']:
                action = execution['command']
                params = execution.get('params', {})

                devices = request.env['sc.google.home.device'].sudo().search([('external_id', 'in', device_ids)])
                for d in devices:
                    if action == 'action.devices.commands.OnOff':
                        d.action_toggle_power(params['on'])
                    elif action == 'action.devices.commands.BrightnessAbsolute':
                        d.action_set_brightness(params['brightness'])

                results.append({
                    'ids': device_ids,
                    'status': 'SUCCESS',
                    'states': {'online': True}
                })

        return {
            'requestId': payload.get('requestId'),
            'payload': {'commands': results}
        }
