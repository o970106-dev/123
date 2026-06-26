import json
import logging
import secrets
from odoo import http
from odoo.http import request
from odoo.addons.pms_base.models.staps_core import staps_timed, MetricTensorCryptoEngine

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/auth', type='http', auth='user')
    def auth(self, **kwargs):
        """Supreme Security OAuth2 Auth Endpoint."""
        redirect_uri = kwargs.get('redirect_uri', '')
        state = kwargs.get('state')

        # Strict Security: Only allow official Google Home redirect URI
        if not redirect_uri.startswith('https://oauth-redirect.googleusercontent.com/'):
            return request.make_response("Forbidden: Invalid redirect_uri", status=403)

        # Generate 32-byte secure authorization code
        auth_code = secrets.token_hex(32)
        request.env.user.sudo().write({'google_home_authorization_code': auth_code})
        return request.redirect(f"{redirect_uri}?code={auth_code}&state={state}")

    @http.route('/google_home/token', type='http', auth='public', methods=['POST'], csrf=False)
    def token(self, **kwargs):
        """Secure OAuth2 Token Endpoint with client verification."""
        params = request.params
        grant_type = params.get('grant_type')
        client_secret = params.get('client_secret')

        # Supreme Security: Validate client_secret (Normally stored in System Parameters)
        # For this optimization, we enforce a secure check
        expected_secret = request.env['ir.config_parameter'].sudo().get_param('pms.google_home_client_secret', 'supreme_secret_v4')
        if client_secret != expected_secret:
            return request.make_response(json.dumps({'error': 'invalid_client'}), status=401, headers=[('Content-Type', 'application/json')])

        if grant_type == 'authorization_code':
            auth_code = params.get('code')
            user = request.env['res.users'].sudo().search([('google_home_authorization_code', '=', auth_code)], limit=1)
            if not user:
                return request.make_response(json.dumps({'error': 'invalid_grant'}), status=400, headers=[('Content-Type', 'application/json')])

            # Generate new secure token and refresh token
            access_token = secrets.token_hex(32)
            refresh_token = secrets.token_hex(32)
            user.write({
                'google_home_token': access_token,
                'google_home_refresh_token': refresh_token,
                'google_home_authorization_code': False # One-time use
            })
        elif grant_type == 'refresh_token':
            r_token = params.get('refresh_token')
            user = request.env['res.users'].sudo().search([('google_home_refresh_token', '=', r_token)], limit=1)
            if not user:
                return request.make_response(json.dumps({'error': 'invalid_grant'}), status=400, headers=[('Content-Type', 'application/json')])
            access_token = secrets.token_hex(32)
            user.write({'google_home_token': access_token})
            refresh_token = r_token
        else:
            return request.make_response(json.dumps({'error': 'unsupported_grant_type'}), status=400, headers=[('Content-Type', 'application/json')])

        data = {
            "token_type": "bearer",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 3600
        }
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
    @staps_timed(persist=True)
    def fulfillment(self, **kwargs):
        """Main Google Smart Home Fulfillment Endpoint."""
        payload = json.loads(request.httprequest.data)
        inputs = payload.get('inputs', [])

        # Security: Verify resident via Authorization header
        auth_header = request.httprequest.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()

        if not token:
            return request.make_response(json.dumps({'requestId': payload.get('requestId'), 'payload': {'errorCode': 'authFailure'}}), headers=[('Content-Type', 'application/json')])

        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)

        if not user:
            return request.make_response(json.dumps({'requestId': payload.get('requestId'), 'payload': {'errorCode': 'authFailure'}}), headers=[('Content-Type', 'application/json')])

        response_payload = {}
        intent = inputs[0].get('intent') if inputs else None

        if intent == 'action.devices.SYNC':
            response_payload = self._handle_sync(user)
        elif intent == 'action.devices.QUERY':
            response_payload = self._handle_query(user, inputs[0].get('payload', {}))
        elif intent == 'action.devices.EXECUTE':
            response_payload = self._handle_execute(user, inputs[0].get('payload', {}))

        res_data = {
            'requestId': payload.get('requestId'),
            'payload': response_payload
        }
        return request.make_response(json.dumps(res_data), headers=[('Content-Type', 'application/json')])

    def _handle_sync(self, user):
        devices = request.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
        device_list = []
        for dev in devices:
            device_list.append({
                'id': dev.google_device_id,
                'type': dev.device_type,
                'traits': dev.get_google_traits(),
                'name': {
                    'name': dev.name,
                    'nicknames': dev.nicknames.split(',') if dev.nicknames else [dev.name],
                    'defaultNames': dev.default_names.split(',') if dev.default_names else [dev.name]
                },
                'willReportState': True,
                'roomHint': dev.room_name,
                'attributes': dev.get_google_attributes(),
                'deviceInfo': {
                    'manufacturer': dev.manufacturer,
                    'model': dev.model_number,
                    'hwVersion': dev.hw_version,
                    'swVersion': dev.sw_version,
                },
                'customData': {
                    'pms_id': dev.id,
                    'pms_id_secure': MetricTensorCryptoEngine.encode(dev.id),
                    'pms_optimization_level': 'Highest Degree',
                    'staps_enabled': True
                }
            })
        return {'agentUserId': MetricTensorCryptoEngine.encode(user.id), 'devices': device_list}

    def _handle_query(self, user, payload):
        device_ids = [d['id'] for d in payload.get('devices', [])]
        devices_status = {}
        for gid in device_ids:
            dev = request.env['pms.device'].sudo().search([('google_device_id', '=', gid), ('resident_id', '=', user.id)], limit=1)
            if dev:
                status = {
                    'online': True,
                    'on': dev.is_on,
                }
                if dev.device_type == 'action.devices.types.LOCK':
                    status['isLocked'] = dev.is_locked
                    status['isJammed'] = False
                elif dev.device_type == 'action.devices.types.THERMOSTAT':
                    status['thermostatTemperatureAmbient'] = dev.temperature
                    status['thermostatTemperatureSetpoint'] = dev.target_temperature
                    status['thermostatMode'] = 'heat' if dev.is_on else 'off'
                elif dev.device_type == 'action.devices.types.SENSOR':
                    status['thermostatTemperatureAmbient'] = dev.temperature
                    status.update({
                        'currentSensorStateData': [
                            {
                                'name': 'HumiditySetting',
                                'rawValue': dev.humidity
                            },
                            {
                                'name': 'OccupancySensing',
                                'currentDescriptiveState': dev.occupancy
                            }
                        ]
                    })

                if 'action.devices.traits.Brightness' in dev.get_google_traits():
                    status['brightness'] = dev.brightness

                if 'action.devices.traits.FanSpeed' in dev.get_google_traits():
                    status['currentFanSpeedSetting'] = 'High' if dev.fan_speed > 50 else 'Low'

                if 'action.devices.traits.ColorTemperature' in dev.get_google_traits():
                    status['color'] = {'temperatureK': dev.color_temp}

                devices_status[gid] = status
        return {'devices': devices_status}

    def _handle_execute(self, user, payload):
        commands = payload.get('commands', [])
        results = []
        for command in commands:
            device_ids = [d['id'] for d in command.get('devices', [])]
            for execution in command.get('execution', []):
                action = execution.get('command')
                params = execution.get('params', {})

                executed_ids = []
                for gid in device_ids:
                    dev = request.env['pms.device'].sudo().search([('google_device_id', '=', gid), ('resident_id', '=', user.id)], limit=1)
                    if dev:
                        if action == 'action.devices.commands.OnOff':
                            dev.is_on = params.get('on')
                        elif action == 'action.devices.commands.BrightnessAbsolute':
                            dev.brightness = params.get('brightness')
                        elif action == 'action.devices.commands.LockUnlock':
                            dev.is_locked = params.get('lock')
                        elif action == 'action.devices.commands.ThermostatTemperatureSetpoint':
                            dev.target_temperature = params.get('thermostatTemperatureSetpoint')
                        elif action == 'action.devices.commands.SetFanSpeed':
                            dev.fan_speed = 100 if params.get('fanSpeed') == 'High' else 30
                        elif action == 'action.devices.commands.ColorAbsolute':
                            dev.color_temp = params.get('colorTemperature')
                        elif action == 'action.devices.commands.ActivateScene':
                            if dev.device_type == 'action.devices.types.SCENE' and 'Eco' in dev.name:
                                user.action_reward_sustainability(amount=5.0, reason="Eco Mode Activation")
                                dev.eco_mode = not params.get('deactivate', False)
                        executed_ids.append(gid)

                results.append({
                    'ids': executed_ids,
                    'status': 'SUCCESS',
                    'states': params
                })
        return {'commands': results}
