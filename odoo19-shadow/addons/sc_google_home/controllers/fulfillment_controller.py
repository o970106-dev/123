import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/auth', type='http', auth='user')
    def auth(self, **kwargs):
        """Secure OAuth2 Auth Endpoint."""
        redirect_uri = kwargs.get('redirect_uri')
        state = kwargs.get('state')
        # In a real scenario, this would redirect to a login/consent page.
        # Here we redirect back with a code if the user is authenticated in Odoo.
        return request.redirect(f"{redirect_uri}?code=secure_code&state={state}")

    @http.route('/google_home/token', type='http', auth='public', methods=['POST'], csrf=False)
    def token(self, **kwargs):
        """Mock OAuth2 Token Endpoint."""
        data = {
            "token_type": "bearer",
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600
        }
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/google_home/fulfillment', type='http', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        """Highest-Degree Google Smart Home Fulfillment Endpoint."""
        try:
            payload = json.loads(request.httprequest.data)
        except Exception:
            return request.make_response(json.dumps({'errorCode': 'protocolError'}), headers=[('Content-Type', 'application/json')])

        inputs = payload.get('inputs', [])

        # Security: Verify resident via Google Home Token on res.users
        auth_header = request.httprequest.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()

        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)

        if not user or not token:
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
                'deviceInfo': {
                    'manufacturer': dev.manufacturer,
                    'model': dev.model_number,
                    'hwVersion': dev.hw_version,
                    'swVersion': dev.sw_version
                },
                'attributes': dev.get_google_attributes()
            })
        return {'agentUserId': str(user.id), 'devices': device_list}

    def _handle_query(self, user, payload):
        device_ids = [d['id'] for d in payload.get('devices', [])]
        devices_status = {}
        for gid in device_ids:
            dev = request.env['pms.device'].sudo().search([('google_device_id', '=', gid), ('resident_id', '=', user.id)], limit=1)
            if dev:
                status = {
                    'online': True,
                    'on': dev.is_on,
                    'brightness': dev.brightness,
                }
                if dev.device_type == 'action.devices.types.LOCK':
                    status['isLocked'] = dev.is_locked
                    status['isJammed'] = False
                elif dev.device_type == 'action.devices.types.THERMOSTAT':
                    status['thermostatTemperatureAmbient'] = dev.temperature
                    status['thermostatTemperatureSetpoint'] = dev.target_temperature
                    status['thermostatMode'] = 'heat' if dev.is_on else 'off'

                status['currentFanSpeedSetting'] = 'High' if dev.fan_speed > 50 else 'Low'
                status['color'] = {'temperatureK': dev.color_temp}

                # Sustainability Metadata
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
                        executed_ids.append(gid)

                results.append({
                    'ids': executed_ids,
                    'status': 'SUCCESS',
                    'states': params
                })
        return {'commands': results}
