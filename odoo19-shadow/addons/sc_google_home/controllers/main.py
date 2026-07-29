import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/fulfillment', type='json', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        payload = request.jsonrequest
        intent = payload.get('inputs', [{}])[0].get('intent')

        # Real token validation
        auth_header = request.httprequest.headers.get('Authorization')
        user = self._get_authenticated_user(auth_header)
        if not user:
            return {'errorCode': 'authFailure'}

        request.update_env(user=user)

        if intent == 'action.devices.SYNC':
            return self._handle_sync(user)
        elif intent == 'action.devices.QUERY':
            return self._handle_query(payload, user)
        elif intent == 'action.devices.EXECUTE':
            return self._handle_execute(payload, user)

        return {'requestId': payload.get('requestId'), 'payload': {}}

    def _get_authenticated_user(self, auth_header):
        if not auth_header:
            return None
        token = auth_header.replace('Bearer ', '')
        # Search for user with this token
        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)
        return user

    def _handle_sync(self, user):
        devices = request.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
        device_list = []
        for d in devices:
            device_list.append({
                'id': str(d.id),
                'type': f"action.devices.types.{d.type.upper()}",
                'traits': ['action.devices.traits.OnOff'],
                'name': {'name': d.name},
                'willReportState': True,
            })
        return {
            'requestId': request.jsonrequest.get('requestId'),
            'payload': {
                'agentUserId': str(user.id),
                'devices': device_list
            }
        }

    def _handle_query(self, payload, user):
        device_ids = [d['id'] for d in payload.get('inputs', [{}])[0].get('payload', {}).get('devices', [])]
        devices = request.env['pms.device'].sudo().search([('id', 'in', device_ids), ('resident_id', '=', user.id)])

        device_states = {}
        for d in devices:
            device_states[str(d.id)] = {
                'on': d.state,
                'online': d.status == 'online'
            }

        return {
            'requestId': payload.get('requestId'),
            'payload': {
                'devices': device_states
            }
        }

    def _handle_execute(self, payload, user):
        commands = payload.get('inputs', [{}])[0].get('payload', {}).get('commands', [])
        results = []
        for command in commands:
            ids = [d.get('id') for d in command.get('devices', [])]
            for execution in command.get('execution', []):
                exec_command = execution.get('command')
                params = execution.get('params')

                if exec_command == 'action.devices.commands.OnOff':
                    new_state = params.get('on')
                    devices = request.env['pms.device'].sudo().search([('id', 'in', ids), ('resident_id', '=', user.id)])
                    devices.write({'state': new_state})

                    results.append({
                        'ids': ids,
                        'status': 'SUCCESS',
                        'states': {'on': new_state, 'online': True}
                    })

        return {
            'requestId': payload.get('requestId'),
            'payload': {'commands': results}
        }
