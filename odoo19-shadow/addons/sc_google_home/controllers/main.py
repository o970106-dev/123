import json
import logging
from odoo import http
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):
    """
    Google Home Fulfillment Controller for PMS.
    IMPORTANT SECURITY NOTE: This implementation uses mocked OAuth2 routes and tokens for demonstration
    and architectural validation purposes. In a production deployment, these routes (/auth, /token)
    MUST be replaced by a secure, industry-standard OAuth2 provider (e.g., Keycloak, Auth0, or Odoo's
    native OAuth2 provider if properly configured).
    """

    def _validate_token(self):
        """
        Validates the Bearer token against the resident user's google_home_token.
        Production Warning: Ensure tokens are stored securely (hashed) and have expiration logic.
        """
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)
        return user

    @http.route('/google_home/auth', type='http', auth='none')
    def auth(self, **kw):
        """Mock OAuth2 Authorization Endpoint."""
        return request.redirect(f"{kw.get('redirect_uri')}?code=mock_code&state={kw.get('state')}")

    @http.route('/google_home/token', type='http', auth='none', csrf=False, methods=['POST'])
    def token(self, **kw):
        """Mock OAuth2 Token Endpoint."""
        # TODO: Implement real token exchange logic for production
        return request.make_response(json.dumps({
            "token_type": "bearer", "access_token": "mock_access_token_123", "expires_in": 3600
        }), headers=[('Content-Type', 'application/json')])

    @http.route('/google_home/fulfillment', type='json', auth='none', csrf=False)
    @staps_timed("google_home_fulfillment", persist=False) # Disable DB persistence for high-frequency fulfillment
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
                'type': 'action.devices.types.LIGHT' if dev.device_type == 'light' else
                        ('action.devices.types.THERMOSTAT' if dev.device_type == 'ac' else 'action.devices.types.LOCK'),
                'traits': dev.get_google_traits(),
                'name': {'name': dev.name},
                'willReportState': True,
                'attributes': dev.get_google_capabilities()
            })
        return {
            'requestId': request.jsonrequest.get('requestId'),
            'payload': {'agentUserId': str(user.id), 'devices': device_list}
        }

    def _handle_query(self, user, payload):
        devices_requested = payload.get('inputs')[0].get('payload').get('devices')
        device_states = {}
        for dr in devices_requested:
            dev_id_str = dr.get('id').split('_')[-1]
            dev = request.env['pms.device'].sudo().search([('id', '=', int(dev_id_str)), ('resident_id', '=', user.id)], limit=1)
            if dev:
                state = {
                    'online': True,
                    'on': dev.state == 'on',
                    'currentSensorStateData': [
                        {'name': 'Happiness Coins', 'numericValue': user.happiness_coin_balance}
                    ]
                }
                if dev.device_type == 'lock':
                    state.update({'isLocked': dev.is_locked, 'isJammed': False})
                if dev.device_type == 'ac':
                    state.update({
                        'thermostatMode': 'cool' if dev.state == 'on' else 'off',
                        'thermostatTemperatureAmbient': dev.temperature,
                        'thermostatTemperatureSetpoint': dev.target_temperature,
                    })
                device_states[dr.get('id')] = state
        return {'requestId': payload.get('requestId'), 'payload': {'devices': device_states}}

    def _handle_execute(self, user, payload):
        commands = payload.get('inputs')[0].get('payload').get('commands')
        results = []
        for command in commands:
            for dev_req in command.get('devices'):
                dev_id_str = dev_req.get('id').split('_')[-1]
                dev = request.env['pms.device'].sudo().search([('id', '=', int(dev_id_str)), ('resident_id', '=', user.id)], limit=1)
                if dev:
                    states = {}
                    for exec_cmd in command.get('execution'):
                        cmd_name = exec_cmd.get('command')
                        params = exec_cmd.get('params')
                        if cmd_name == 'action.devices.commands.OnOff':
                            dev.write({'state': 'on' if params.get('on') else 'off'})
                            states['on'] = dev.state == 'on'
                        elif cmd_name == 'action.devices.commands.LockUnlock':
                            dev.write({'is_locked': params.get('lock')})
                            states['isLocked'] = dev.is_locked
                        elif cmd_name == 'action.devices.commands.ThermostatTemperatureSetpoint':
                            dev.write({'target_temperature': params.get('thermostatTemperatureSetpoint')})
                            states['thermostatTemperatureSetpoint'] = dev.target_temperature
                    results.append({'ids': [dev_req.get('id')], 'status': 'SUCCESS', 'states': states})
                else:
                    results.append({'ids': [dev_req.get('id')], 'status': 'ERROR', 'errorCode': 'deviceNotFound'})
        return {'requestId': payload.get('requestId'), 'payload': {'commands': results}}
