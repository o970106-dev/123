from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    def _validate_auth(self):
        """
        Validates the Authorization header against Odoo System Parameters.
        """
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            _logger.warning("Missing or invalid Authorization header")
            return False

        token = auth_header.split(' ')[1]

        # Fetch expected token from System Parameters
        expected_token = request.env['ir.config_parameter'].sudo().get_param('sc_google_home.bearer_token')

        if not expected_token:
            _logger.error("Google Home Bearer Token is not configured in System Parameters (sc_google_home.bearer_token)")
            return False

        if token != expected_token:
            _logger.warning("Invalid Google Home Bearer Token received")
            return False

        return True

    @http.route('/google_home/fulfillment', type='json', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        # SECURITY: Mandatory authentication check
        if not self._validate_auth():
            # Attempt to get requestId from dispatcher if possible
            req_data = {}
            try:
                # In Odoo, json request is already parsed in request.dispatcher.jsonrequest (v17+)
                # or request.params for older versions.
                req_data = request.dispatcher.jsonrequest
            except:
                pass

            return {
                'requestId': req_data.get('requestId'),
                'payload': {
                    'errorCode': 'authFailure'
                }
            }

        payload = request.dispatcher.jsonrequest
        inputs = payload.get('inputs', [{}])
        if not inputs:
            return {'requestId': payload.get('requestId'), 'payload': {'errorCode': 'protocolError'}}

        intent = inputs[0].get('intent')
        request_id = payload.get('requestId')

        _logger.info("Validated Google Home Intent: %s", intent)

        try:
            if intent == 'action.devices.SYNC':
                return self._handle_sync(request_id)
            elif intent == 'action.devices.QUERY':
                return self._handle_query(request_id, inputs[0].get('payload'))
            elif intent == 'action.devices.EXECUTE':
                return self._handle_execute(request_id, inputs[0].get('payload'))
            elif intent == 'action.devices.DISCONNECT':
                return {'requestId': request_id, 'payload': {}}
        except Exception as e:
            _logger.error("Error handling Google Home intent %s: %s", intent, str(e), exc_info=True)
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
        # agentUserId identifies the user to Google. Use database UUID for consistency.
        agent_user_id = request.env['ir.config_parameter'].sudo().get_param('database.uuid') or 'pms-default-user'

        # Fetch devices from Odoo model
        devices = request.env['sc.google.home.device'].sudo().search([])
        device_list = []
        for dev in devices:
            device_list.append({
                'id': str(dev.id),
                'type': dev.device_type,
                'traits': dev.traits.split(','),
                'name': {
                    'name': dev.name,
                    'nicknames': [dev.name],
                    'defaultNames': [dev.name]
                },
                'willReportState': True,
                'deviceInfo': {
                    'manufacturer': 'SmartControl-PMS Authority',
                    'model': 'v2.0-Optimized',
                    'hwVersion': '1.0',
                    'swVersion': '2.0'
                }
            })

        return {
            'requestId': request_id,
            'payload': {
                'agentUserId': agent_user_id,
                'devices': device_list
            }
        }

    def _handle_query(self, request_id, payload):
        device_ids = [d['id'] for d in payload.get('devices', [])]
        devices = request.env['sc.google.home.device'].sudo().browse([int(did) for did in device_ids if did.isdigit()])

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

                devices = request.env['sc.google.home.device'].sudo().browse([int(did) for did in device_ids if did.isdigit()])
                executed_ids = []
                for dev in devices:
                    if dev.exists():
                        dev._execute_google_home_command(action, params)
                        executed_ids.append(str(dev.id))

                if executed_ids:
                    # In a real sync, we should return the updated states
                    results.append({
                        'ids': executed_ids,
                        'status': 'SUCCESS',
                        'states': devices[0]._get_google_home_state() if len(devices) == 1 else {'online': True}
                    })

        return {
            'requestId': request_id,
            'payload': {
                'commands': results
            }
        }
