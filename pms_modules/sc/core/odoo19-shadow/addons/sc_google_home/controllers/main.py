import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        payload = json.loads(request.httprequest.data)
        _logger.info("Google Home Request: %s", json.dumps(payload))

        intent = payload.get('inputs', [{}])[0].get('intent')
        request_id = payload.get('requestId')

        res_data = {}
        if intent == 'action.devices.SYNC':
            res_data = self._handle_sync(request_id)
        elif intent == 'action.devices.QUERY':
            res_data = self._handle_query(request_id, payload.get('inputs', [{}])[0].get('payload', {}))
        elif intent == 'action.devices.EXECUTE':
            res_data = self._handle_execute(request_id, payload.get('inputs', [{}])[0].get('payload', {}))
        else:
            res_data = {
                'requestId': request_id,
                'payload': {
                    'errorCode': 'notSupported'
                }
            }

        return request.make_response(
            json.dumps(res_data),
            headers=[('Content-Type', 'application/json')]
        )

    def _handle_sync(self, request_id):
        # Placeholder for SYNC logic
        return {
            'requestId': request_id,
            'payload': {
                'agentUserId': 'user_123',
                'devices': [{
                    'id': 'light_1',
                    'type': 'action.devices.types.LIGHT',
                    'traits': [
                        'action.devices.traits.OnOff',
                        'action.devices.traits.Brightness'
                    ],
                    'name': {
                        'name': '客廳燈'
                    },
                    'willReportState': True
                }]
            }
        }

    def _handle_query(self, request_id, payload):
        # Placeholder for QUERY logic
        return {
            'requestId': request_id,
            'payload': {
                'devices': {
                    'light_1': {
                        'online': True,
                        'on': True,
                        'brightness': 80
                    }
                }
            }
        }

    def _handle_execute(self, request_id, payload):
        # Placeholder for EXECUTE logic
        commands = payload.get('commands', [])
        results = []
        for command in commands:
            for device in command.get('devices', []):
                results.append({
                    'ids': [device.get('id')],
                    'status': 'SUCCESS',
                    'states': {
                        'online': True
                    }
                })

        return {
            'requestId': request_id,
            'payload': {
                'commands': results
            }
        }
