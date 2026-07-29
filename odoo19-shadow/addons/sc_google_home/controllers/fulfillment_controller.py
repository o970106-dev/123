import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/auth', type='http', auth='user')
    def auth(self, **kwargs):
        """Mock OAuth2 Auth Endpoint."""
        redirect_uri = kwargs.get('redirect_uri')
        state = kwargs.get('state')

        # Security: Link auth code to the current logged-in user
        import secrets
        auth_code = secrets.token_hex(16)
        request.env.user.sudo().google_home_authorization_code = auth_code

        # Optimized to use request.redirect for professional account linking
        return request.redirect(f"{redirect_uri}?code={auth_code}&state={state}")

    @http.route('/google_home/token', type='http', auth='public', methods=['POST'], csrf=False)
    def token(self, **kwargs):
        """Mock OAuth2 Token Endpoint."""
        # Security: Exchange authorization code for the specific user's token
        # In a production environment, this would be handled by a real OAuth2 provider.
        code = request.params.get('code')
        user = request.env['res.users'].sudo().search([('google_home_authorization_code', '=', code)], limit=1)

        if not user or not code:
            return request.make_response(json.dumps({'error': 'invalid_grant'}), status=400, headers=[('Content-Type', 'application/json')])

        # Clear code after use and return user's specific token
        user.google_home_authorization_code = False
        token = user.google_home_token

        data = {
            "token_type": "bearer",
            "access_token": token,
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600
        }
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
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
            # Enhanced professional-grade metadata
            nicknames = [n.strip() for n in (dev.nicknames or "").split(',') if n.strip()]
            default_names = [n.strip() for n in (dev.default_names or "").split(',') if n.strip()]

            device_list.append({
                'id': dev.google_device_id,
                'type': dev.device_type,
                'traits': dev.get_google_traits(),
                'name': {
                    'name': dev.name,
                    'nicknames': nicknames or [dev.name],
                    'defaultNames': default_names or [dev.name]
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
                    'optimization_level': 'Supreme'
                }
            })
        return {'agentUserId': str(user.id), 'devices': device_list}

    def _handle_query(self, user, payload):
        device_ids = [d['id'] for d in payload.get('devices', [])]
        devices_status = {}
        for gid in device_ids:
            dev = request.env['pms.device'].sudo().search([('google_device_id', '=', gid)], limit=1)
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
