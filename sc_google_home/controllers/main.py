import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/fulfillment', type='json', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        # Note: In production, you MUST verify the OAuth2 Bearer token here.
        # This is a simplified draft.

        data = request.jsonrequest
        intent = data.get('inputs', [{}])[0].get('intent')
        request_id = data.get('requestId')

        _logger.info("Received Google Home intent: %s", intent)

        if intent == 'action.devices.SYNC':
            return self._handle_sync(request_id)
        elif intent == 'action.devices.QUERY':
            return self._handle_query(request_id, data)
        elif intent == 'action.devices.EXECUTE':
            return self._handle_execute(request_id, data)
        elif intent == 'action.devices.DISCONNECT':
            return self._handle_disconnect(request_id)

        return {'requestId': request_id, 'payload': {'error': 'notSupported'}}

    def _handle_sync(self, request_id):
        devices = request.env['smart.device'].sudo().search([])
        device_list = []
        for dev in devices:
            device_list.append({
                'id': str(dev.id),
                'type': dev.device_type,
                'traits': ['action.devices.traits.OnOff'],
                'name': {'name': dev.name},
                'willReportState': False,
            })

        return {
            'requestId': request_id,
            'payload': {
                'agentUserId': str(request.uid or '1'),
                'devices': device_list
            }
        }

    def _handle_query(self, request_id, data):
        device_ids = [d['id'] for d in data.get('inputs', [{}])[0].get('payload', {}).get('devices', [])]
        devices = request.env['smart.device'].sudo().browse([int(did) for did in device_ids if did.isdigit()])

        response_devices = {}
        for dev in devices:
            response_devices[str(dev.id)] = {
                'online': True,
                'on': dev.state,
                'brightness': dev.brightness if dev.device_type == 'action.devices.types.LIGHT' else None
            }

        return {
            'requestId': request_id,
            'payload': {'devices': response_devices}
        }

    def _handle_execute(self, request_id, data):
        commands = data.get('inputs', [{}])[0].get('payload', {}).get('commands', [])
        results = []

        for command in commands:
            ids = [int(d['id']) for d in command.get('devices', []) if d['id'].isdigit()]
            for execution in command.get('execution', []):
                action = execution.get('command')
                params = execution.get('params', {})

                devices = request.env['smart.device'].sudo().browse(ids)
                if action == 'action.devices.commands.OnOff':
                    devices.write({'state': params.get('on')})
                elif action == 'action.devices.commands.BrightnessAbsolute':
                    devices.write({'brightness': params.get('brightness')})

                results.append({
                    'ids': [str(i) for i in ids],
                    'status': 'SUCCESS',
                    'states': {
                        'online': True,
                        'on': params.get('on') if 'on' in params else None
                    }
                })

        return {
            'requestId': request_id,
            'payload': {'commands': results}
        }

    def _handle_disconnect(self, request_id):
        return {}
