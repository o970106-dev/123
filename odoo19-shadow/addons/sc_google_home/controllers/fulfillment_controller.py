import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/auth', type='http', auth='public')
    def auth(self, **kwargs):
        """Mock OAuth2 Auth Endpoint with XSS protection."""
        from werkzeug.utils import redirect
        from markupsafe import escape
        redirect_uri = kwargs.get('redirect_uri')
        state = kwargs.get('state')
        # In a real scenario, this would render a login page.
        if redirect_uri:
            # For mock purposes, we just redirect back with a code.
            # Security: Ensure we're not just blindly redirecting to any URL.
            return f"Redirecting to <a href='{escape(redirect_uri)}?code=mock_code&state={escape(state)}'>{escape(redirect_uri)}</a>"
        return "Invalid Request"

    @http.route('/google_home/token', type='http', auth='public', methods=['POST'], csrf=False)
    def token(self, **kwargs):
        """Mock OAuth2 Token Endpoint."""
        # Note: In a production environment, this should interface with an Odoo OAuth2 provider.
        data = {
            "token_type": "bearer",
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600
        }
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        """Main Google Smart Home Fulfillment Endpoint."""
        try:
            payload = json.loads(request.httprequest.data)
        except Exception:
            return request.make_response(json.dumps({'error': 'invalid_request'}), headers=[('Content-Type', 'application/json')])

        requestId = payload.get('requestId')
        inputs = payload.get('inputs', [])

        # Security: Verify resident via Authorization header
        auth_header = request.httprequest.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()

        if not token:
            _logger.warning("Fulfillment: Missing Authorization Token")
            return self._make_google_error(requestId, 'authFailure')

        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)

        if not user:
            _logger.warning(f"Fulfillment: Invalid Token {token}")
            return self._make_google_error(requestId, 'authFailure')

        response_payload = {}
        intent = inputs[0].get('intent') if inputs else None

        if intent == 'action.devices.SYNC':
            response_payload = self._handle_sync(user)
        elif intent == 'action.devices.QUERY':
            response_payload = self._handle_query(user, inputs[0].get('payload', {}))
        elif intent == 'action.devices.EXECUTE':
            response_payload = self._handle_execute(user, inputs[0].get('payload', {}))

        res_data = {
            'requestId': requestId,
            'payload': response_payload
        }
        return request.make_response(json.dumps(res_data), headers=[('Content-Type', 'application/json')])

    def _make_google_error(self, requestId, errorCode):
        """Helper to create protocol-compliant error responses."""
        res_data = {
            'requestId': requestId,
            'payload': {'errorCode': errorCode}
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
                'name': {'name': dev.name},
                'willReportState': True,
                'roomHint': dev.room_name,
                'attributes': dev.get_google_attributes()
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
