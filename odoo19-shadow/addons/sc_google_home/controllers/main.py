import json
import logging
from odoo import http
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):
    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
    @staps_timed
    def fulfillment(self, **kwargs):
        data = json.loads(request.httprequest.data)
        _logger.info(f"[GoogleHome] Received fulfillment intent: {data.get('inputs', [{}])[0].get('intent')}")

        token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)

        if not user:
            return request.make_response(json.dumps({'status': 'error', 'message': 'Unauthorized'}), [('Content-Type', 'application/json')], status=401)

        intent = data['inputs'][0]['intent']
        payload = {}

        if intent == 'action.devices.SYNC':
            payload = self._handle_sync(user)
        elif intent == 'action.devices.QUERY':
            payload = self._handle_query(user, data['inputs'][0]['payload'])
        elif intent == 'action.devices.EXECUTE':
            payload = self._handle_execute(user, data['inputs'][0]['payload'])

        response = {
            'requestId': data['requestId'],
            'payload': payload
        }
        return request.make_response(json.dumps(response), [('Content-Type', 'application/json')])

    def _handle_sync(self, user):
        devices = request.env['sc.google.home.device'].sudo().search([('resident_id', '=', user.id)])
        sync_devices = []
        for d in devices:
            traits = ['action.devices.traits.OnOff']
            if d.device_type == 'lock':
                traits.append('action.devices.traits.LockUnlock')
            elif d.device_type == 'sensor':
                traits.append('action.devices.traits.SensorState')

            sync_devices.append({
                'id': d.google_device_id,
                'type': f'action.devices.types.{d.device_type.upper()}',
                'traits': traits,
                'name': {'name': d.name},
                'willReportState': True,
                'attributes': self._get_attributes(d)
            })
        return {'agentUserId': str(user.id), 'devices': sync_devices}

    def _get_attributes(self, device):
        if device.device_type == 'sensor':
            return {
                "sensorStates": [
                    {
                        "name": "Happiness Coins",
                        "numericCapabilities": {
                            "unit": "COIN"
                        },
                        "feature": "COMMUNITY_SCORE"
                    }
                ]
            }
        return {}

    def _handle_query(self, user, payload):
        device_ids = [d['id'] for d in payload['devices']]
        # Security: Filter by resident_id
        devices = request.env['sc.google.home.device'].sudo().search([
            ('google_device_id', 'in', device_ids),
            ('resident_id', '=', user.id)
        ])
        query_results = {}
        for d in devices:
            state = {'online': True}
            if d.device_id:
                state['on'] = d.device_id.is_on
                if d.device_type == 'lock':
                    state['isLocked'] = not d.device_id.is_on
            elif d.device_type == 'sensor':
                # Map partner to coin balance
                balance = user.partner_id.happiness_coin_balance if hasattr(user.partner_id, 'happiness_coin_balance') else 100
                state['currentSensorStateData'] = [{
                    'name': 'Happiness Coins',
                    'currentSensorState': 'score',
                    'rawValue': balance
                }]
            query_results[d.google_device_id] = state
        return {'devices': query_results}

    def _handle_execute(self, user, payload):
        commands_results = []
        for command in payload['commands']:
            device_ids = [d['id'] for d in command['devices']]
            execution = command['execution'][0]
            action = execution['command']
            params = execution.get('params', {})

            ids = []
            for dev_id in device_ids:
                # Security: Filter by resident_id
                device = request.env['sc.google.home.device'].sudo().search([
                    ('google_device_id', '=', dev_id),
                    ('resident_id', '=', user.id)
                ], limit=1)
                if device and device.device_id:
                    if action == 'action.devices.commands.OnOff':
                        device.device_id.write({'is_on': params['on']})
                    elif action == 'action.devices.commands.LockUnlock':
                        device.device_id.write({'is_on': not params['lock']})
                    ids.append(dev_id)

            commands_results.append({
                'ids': ids,
                'status': 'SUCCESS',
                'states': {'online': True}
            })
        return {'commands': commands_results}
