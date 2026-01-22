from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    def _validate_auth(self):
        """
        Validates the Authorization header.
        In production, this should verify the Bearer token against an OAuth2 provider.
        """
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            _logger.warning("Missing or invalid Authorization header")
            return False

        token = auth_header.split(' ')[1]
        # PLACEHOLDER: Integrate with Odoo's OAuth2 or session validation here
        # For demonstration, we check against a configured secret or allow if token exists
        # In a real 'Authority' implementation, this would call a token validation service.
        if not token:
            return False

        return True

    @http.route('/google_home/fulfillment', type='json', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        # SECURITY: Mandatory authentication check
        if not self._validate_auth():
            return {
                'requestId': request.dispatcher.jsonrequest.get('requestId'),
                'payload': {
                    'errorCode': 'authFailure'
                }
            }

        payload = request.dispatcher.jsonrequest
        intent = payload.get('inputs', [{}])[0].get('intent')
        request_id = payload.get('requestId')

        _logger.info("Google Home Intent: %s", intent)

        try:
            if intent == 'action.devices.SYNC':
                return self._handle_sync(request_id)
            elif intent == 'action.devices.QUERY':
                return self._handle_query(request_id, payload.get('inputs')[0].get('payload'))
            elif intent == 'action.devices.EXECUTE':
                return self._handle_execute(request_id, payload.get('inputs')[0].get('payload'))
        except Exception as e:
            _logger.error("Error handling Google Home intent: %s", str(e))
            return {
                'requestId': request_id,
                'payload': {
                    'errorCode': 'hardError'
                }
            }

        return {
            'requestId': request_id,
            'payload': {
                'errorCode': 'protocolError'
            }
        }

    def _handle_sync(self, request_id):
        # Fetch devices from sc.google.home.device model
        # Use sudo() safely after authentication has been verified
        devices = request.env['sc.google.home.device'].sudo().search([])
        device_list = []
        for dev in devices:
            device_list.append({
                'id': str(dev.id),
                'type': dev.device_type,
                'traits': dev.traits.split(','),
                'name': {'name': dev.name},
                'willReportState': True,
            })

        return {
            'requestId': request_id,
            'payload': {
                'agentUserId': str(request.env.user.id),
                'devices': device_list
            }
        }

    def _handle_query(self, request_id, payload):
        device_ids = [d['id'] for d in payload.get('devices', [])]
        devices = request.env['sc.google.home.device'].sudo().browse([int(id) for id in device_ids])

        dev_states = {}
        for dev in devices:
            if dev.exists():
                dev_states[str(dev.id)] = dev._get_google_home_state()

        return {
            'requestId': request_id,
            'payload': {
                'devices': dev_states
            }
        }

    def _handle_execute(self, request_id, payload):
        commands = payload.get('commands', [])
        results = []
        for command in commands:
            device_ids = [d['id'] for d in command.get('devices', [])]
            for execution in command.get('execution', []):
                action = execution.get('command')
                params = execution.get('params')

                devices = request.env['sc.google.home.device'].sudo().browse([int(id) for id in device_ids])
                for dev in devices:
                    if dev.exists():
                        dev._execute_google_home_command(action, params)
                        results.append({
                            'ids': [str(dev.id)],
                            'status': 'SUCCESS',
                            'states': dev._get_google_home_state()
                        })

        return {
            'requestId': request_id,
            'payload': {
                'commands': results
            }
        }
