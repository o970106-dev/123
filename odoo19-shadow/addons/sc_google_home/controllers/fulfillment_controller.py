import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GoogleHomeFulfillment(http.Controller):

    @http.route('/google_home/auth', type='http', auth='public')
    def auth(self, **kwargs):
        """Mock OAuth2 Auth Endpoint."""
        redirect_uri = kwargs.get('redirect_uri')
        state = kwargs.get('state')
        return f"Redirecting to <a href='{redirect_uri}?code=mock_code&state={state}'>{redirect_uri}</a>"

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

    @http.route('/google_home/fulfillment', type='json', auth='public', methods=['POST'], csrf=False)
    def fulfillment(self, **kwargs):
        """Main Google Smart Home Fulfillment Endpoint."""
        payload = request.get_json_data()
        inputs = payload.get('inputs', [])

        # Security: Verify resident via Authorization header
        auth_header = request.httprequest.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()

        user = request.env['res.users'].sudo().search([('google_home_token', '=', token)], limit=1)
        if not user and token == 'mock_access_token':
            # Fallback for demonstration/testing with the mock token
            user = request.env['res.users'].sudo().search([('id', '=', 2)], limit=1)

        if not user:
            return {'errorCode': 'authFailure'}

        response_payload = {}
        intent = inputs[0].get('intent') if inputs else None

        if intent == 'action.devices.SYNC':
            response_payload = self._handle_sync(user)
        elif intent == 'action.devices.QUERY':
            response_payload = self._handle_query(user, inputs[0].get('payload', {}))
        elif intent == 'action.devices.EXECUTE':
            response_payload = self._handle_execute(user, inputs[0].get('payload', {}))

        return {
            'requestId': payload.get('requestId'),
            'payload': response_payload
        }

    def _handle_sync(self, user):
        devices = request.env['pms.device'].sudo().search([('resident_id', '=', user.id)])
        device_list = []
        for dev in devices:
            traits = ['action.devices.traits.OnOff']
            if dev.device_type == 'action.devices.types.LOCK':
                traits.append('action.devices.traits.LockUnlock')
            elif dev.device_type == 'action.devices.types.THERMOSTAT':
                traits.append('action.devices.traits.TemperatureSetting')

            # Community Score via SensorState
            traits.append('action.devices.traits.SensorState')

            device_list.append({
                'id': dev.google_device_id,
                'type': dev.device_type,
                'traits': traits,
                'name': {'name': dev.name},
                'willReportState': True,
                'attributes': {
                    'sensorStates': [
                        {
                            'name': 'Happiness Coins',
                            'numericCapabilities': {'unit': 'COIN'},
                            'feature': 'COMMUNITY_SCORE'
                        }
                    ]
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
                        executed_ids.append(gid)

                results.append({
                    'ids': executed_ids,
                    'status': 'SUCCESS',
                    'states': params
                })
        return {'commands': results}
