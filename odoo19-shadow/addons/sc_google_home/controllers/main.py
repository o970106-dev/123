import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):
    def _validate_token(self):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)
        return user

    @http.route('/google_home/auth', type='http', auth='none')
    def auth(self, **kw):
        return request.redirect(f"{kw.get('redirect_uri')}?code=mock_code&state={kw.get('state')}")

    @http.route('/google_home/token', type='http', auth='none', csrf=False, methods=['POST'])
    def token(self, **kw):
        return request.make_response(json.dumps({
            "token_type": "bearer", "access_token": "mock_access_token_123", "expires_in": 3600
        }), headers=[('Content-Type', 'application/json')])

    @http.route('/google_home/fulfillment', type='json', auth='none', csrf=False)
    def fulfillment(self, **kw):
        user = self._validate_token()
        if not user:
            return {'requestId': request.jsonrequest.get('requestId'), 'payload': {'errorCode': 'authFailure'}}

        payload = request.jsonrequest
        intent = payload.get('inputs', [{}])[0].get('intent')
        if intent == 'action.devices.SYNC': return self._handle_sync(user)
        if intent == 'action.devices.QUERY': return self._handle_query(user, payload)
        if intent == 'action.devices.EXECUTE': return self._handle_execute(user, payload)
        return {'requestId': payload.get('requestId'), 'payload': {'errorCode': 'notSupported'}}

    def _handle_sync(self, user):
        devices = request.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
        device_list = []
        for dev in devices:
            device_list.append({
                'id': dev.google_device_id,
                'type': 'action.devices.types.LIGHT',
                'traits': dev.get_google_traits(),
                'name': {'name': dev.name},
                'willReportState': True,
                'attributes': dev.get_google_capabilities() if hasattr(dev, 'get_google_capabilities') else {}
            })
        return {
            'requestId': request.jsonrequest.get('requestId'),
            'payload': {'agentUserId': str(user.id), 'devices': device_list}
        }

    def _handle_query(self, user, payload):
        devices_requested = payload.get('inputs')[0].get('payload').get('devices')
        device_states = {}
        for dr in devices_requested:
            dev_id = int(dr.get('id').split('_')[-1])
            dev = request.env['pms.device'].sudo().search([('id', '=', dev_id), ('resident_id', '=', user.id)], limit=1)
            if dev:
                device_states[dr.get('id')] = {
                    'online': True,
                    'on': dev.state == 'on',
                    'currentSensorStateData': [
                        {'name': 'Happiness Coins', 'numericValue': user.happiness_coin_balance}
                    ]
                }
        return {'requestId': payload.get('requestId'), 'payload': {'devices': device_states}}

    def _handle_execute(self, user, payload):
        commands = payload.get('inputs')[0].get('payload').get('commands')
        results = []
        for command in commands:
            for dev_req in command.get('devices'):
                dev_id = int(dev_req.get('id').split('_')[-1])
                dev = request.env['pms.device'].sudo().search([('id', '=', dev_id), ('resident_id', '=', user.id)], limit=1)
                if dev:
                    for exec_cmd in command.get('execution'):
                        if exec_cmd.get('command') == 'action.devices.commands.OnOff':
                            new_state = 'on' if exec_cmd.get('params').get('on') else 'off'
                            dev.write({'state': new_state})
                    results.append({'ids': [dev_req.get('id')], 'status': 'SUCCESS', 'states': {'on': dev.state == 'on'}})
                else:
                    results.append({'ids': [dev_req.get('id')], 'status': 'ERROR', 'errorCode': 'deviceNotFound'})
        return {'requestId': payload.get('requestId'), 'payload': {'commands': results}}
