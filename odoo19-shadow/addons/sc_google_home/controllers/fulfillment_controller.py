import json
import logging
import werkzeug.utils
from odoo import http
from odoo.http import request
from odoo.tools import html_escape

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/auth', type='http', auth='user', website=True)
    def auth(self, **kwargs):
        """Mock OAuth2 Auth Endpoint with XSS protection."""
        redirect_uri = kwargs.get('redirect_uri')
        state = kwargs.get('state')

        if not redirect_uri:
            return "Missing redirect_uri"

        # Securely redirect with escaped parameters
        params = werkzeug.urls.url_encode({
            'code': 'mock_code',
            'state': state
        })
        return werkzeug.utils.redirect(f"{redirect_uri}?{params}")

    @http.route('/google_home/token', type='http', auth='public', methods=['POST'], csrf=False)
    def token(self, **kwargs):
        """Mock OAuth2 Token Endpoint with functional linking."""
        # In a real flow, the 'code' would be exchanged for a user
        # For this highest-degree mock, we link the token to the admin user (ID 2) for testing
        admin_user = request.env['res.users'].sudo().browse(2)
        token = "mock_access_token"
        admin_user.google_home_token = token

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
                elif dev.device_type == 'action.devices.types.LIGHT':
                    status['brightness'] = dev.brightness
                    status['color'] = {'temperatureK': dev.color_temp}

                status['currentFanSpeedSetting'] = 'High' if dev.fan_speed > 50 else 'Low'

                # Happiness Coins Balance
                status['currentSensorStateData'] = [{
                    'name': 'Happiness Coins',
                    'rawValue': user.happiness_coin_balance
                }]
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
                        elif action == 'action.devices.commands.LockUnlock':
                            dev.is_locked = params.get('lock')
                        elif action == 'action.devices.commands.ThermostatTemperatureSetpoint':
                            dev.target_temperature = params.get('thermostatTemperatureSetpoint')
                        elif action == 'action.devices.commands.SetFanSpeed':
                            dev.fan_speed = 100 if params.get('fanSpeed') == 'High' else 30
                        elif action == 'action.devices.commands.ColorAbsolute':
                            dev.color_temp = params.get('colorTemperature')
                        elif action == 'action.devices.commands.BrightnessAbsolute':
                            dev.brightness = params.get('brightness')
                        elif action == 'action.devices.commands.ActivateScene':
                            dev.eco_mode = not params.get('deactivate', False)
                            if dev.eco_mode:
                                user.action_reward_sustainability(amount=5.0, reason="Google Home Eco Scene")
                        executed_ids.append(gid)

                results.append({
                    'ids': executed_ids,
                    'status': 'SUCCESS',
                    'states': params
                })
        return {'commands': results}
