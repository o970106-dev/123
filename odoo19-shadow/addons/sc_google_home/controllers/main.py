import json
import logging
from odoo import http
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/auth', type='http', auth='public')
    def authorize(self, **kwargs):
        """Mock OAuth2 Authorization Endpoint."""
        # In a real system, this would redirect to Odoo login and then back with a code.
        redirect_uri = kwargs.get('redirect_uri')
        state = kwargs.get('state')
        # We use a simple redirect for this mock
        return request.redirect(f"{redirect_uri}?code=MOCK_CODE&state={state}")

    @http.route('/google_home/token', type='http', auth='public', methods=['POST'], csrf=False)
    def token(self, **kwargs):
        """Mock OAuth2 Token Endpoint."""
        # In a real system, this would exchange the code for an access token and refresh token.
        data = {
            "token_type": "bearer",
            "access_token": "MOCK_ACCESS_TOKEN",
            "refresh_token": "MOCK_REFRESH_TOKEN",
            "expires_in": 3600
        }
        return request.make_response(json.dumps(data), [('Content-Type', 'application/json')])

    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
    @staps_timed
    def fulfillment(self, **kwargs):
        data = json.loads(request.httprequest.data)
        intent = data.get('inputs', [{}])[0].get('intent')
        _logger.info(f"[GoogleHome] Intent: {intent}")

        # In production, verify the Bearer token properly via OAuth2 logic.
        token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
        # For demo purposes, we still look for the token on the user.
        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)

        if not user and token != "MOCK_ACCESS_TOKEN":
            return request.make_response(json.dumps({'status': 'error', 'message': 'Unauthorized'}), [('Content-Type', 'application/json')], status=401)

        # If using mock token, use a default admin or first user for demo.
        if not user:
            user = request.env['res.users'].sudo().search([], limit=1)

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
            device_type = d.device_type or 'LIGHT'

            if d.device_type == 'lock':
                traits.append('action.devices.traits.LockUnlock')
            elif d.device_type == 'sensor':
                traits.append('action.devices.traits.SensorState')
            elif d.device_type == 'thermostat':
                traits.append('action.devices.traits.TemperatureSetting')
            elif d.device_type == 'fan':
                traits.append('action.devices.traits.FanSpeed')

            sync_devices.append({
                'id': d.google_device_id,
                'type': f'action.devices.types.{device_type.upper()}',
                'traits': traits,
                'name': {'name': d.name},
                'willReportState': True,
                'attributes': self._get_attributes(d)
            })
        return {'agentUserId': str(user.id), 'devices': sync_devices}

    def _get_attributes(self, device):
        if device.device_type == 'sensor':
            return {
                "sensorStates": [{
                    "name": "Happiness Coins",
                    "numericCapabilities": {"unit": "COIN"},
                    "feature": "COMMUNITY_SCORE"
                }]
            }
        elif device.device_type == 'thermostat':
            return {
                "availableThermostatModes": "off,heat,cool,on",
                "thermostatTemperatureUnit": "C"
            }
        return {}

    def _handle_query(self, user, payload):
        device_ids = [d['id'] for d in payload['devices']]
        devices = request.env['sc.google.home.device'].sudo().search([('google_device_id', 'in', device_ids)])
        query_results = {}
        for d in devices:
            state = {'online': True, 'status': 'SUCCESS'}
            if d.device_id:
                state['on'] = d.device_id.is_on
                if d.device_type == 'lock':
                    state['isLocked'] = not d.device_id.is_on
                    state['isJammed'] = False
            elif d.device_type == 'sensor':
                state['currentSensorStateData'] = [{
                    'name': 'Happiness Coins',
                    'currentSensorState': 'score',
                    'rawValue': user.happiness_coin_balance
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

            success_ids = []
            for dev_id in device_ids:
                device = request.env['sc.google.home.device'].sudo().search([('google_device_id', '=', dev_id)], limit=1)
                if device and device.device_id:
                    if action == 'action.devices.commands.OnOff':
                        device.device_id.write({'is_on': params['on']})
                        success_ids.append(dev_id)
                    elif action == 'action.devices.commands.LockUnlock':
                        device.device_id.write({'is_on': not params['lock']})
                        success_ids.append(dev_id)

            commands_results.append({
                'ids': success_ids,
                'status': 'SUCCESS',
                'states': {'online': True}
            })
        return {'commands': commands_results}
