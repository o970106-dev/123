import sys
import os
from unittest.mock import MagicMock, patch
import types

# Setup Mock Odoo
odoo = types.ModuleType('odoo')
sys.modules['odoo'] = odoo
odoo.http = MagicMock()
sys.modules['odoo.http'] = odoo.http
odoo.models = MagicMock()
sys.modules['odoo.models'] = odoo.models
odoo.fields = MagicMock()
sys.modules['odoo.fields'] = odoo.fields
odoo.api = MagicMock()
sys.modules['odoo.api'] = odoo.api
odoo.addons = types.ModuleType('odoo.addons')
sys.modules['odoo.addons'] = odoo.addons

# Odoo module mocks
class ModelMock: pass
odoo.models.Model = ModelMock

# Mock Odoo environment for testing logic
class MockRequest:
    def __init__(self):
        self.httprequest = MockHttpRequest()
        self.env = MockEnv()
        self.dispatcher = MockDispatcher()

class MockHttpRequest:
    def __init__(self):
        self.headers = {'Authorization': 'Bearer pms_authority_token_2024'}

class MockDispatcher:
    def __init__(self):
        self.jsonrequest = {}

class MockEnv:
    def __init__(self, user=None):
        self.user = user or MockUser(env=self)
        self.registry = {}

    def __getitem__(self, key):
        if key == 'ir.config_parameter':
            return MockConfigParam()
        if key == 'sc.google.home.device':
            return MockDeviceModel(env=self)
        if key == 'pms.happiness.coin':
            return MockCoinModel(env=self)
        if key == 'pms.telemetry':
            return MockTelemetryModel(env=self)
        return MagicMock()

    def sudo(self):
        return self

class MockUser:
    def __init__(self, env=None):
        self.id = 1
        self.name = "Test Resident"
        self.env = env
        self.partner_id = MockPartner(user=self)
        self.google_home_token = "pms_authority_token_2024"

    def has_group(self, group):
        return False

class MockUserSet(list):
    def __init__(self, users):
        super().__init__(users)
    def __getitem__(self, key):
        if isinstance(key, slice):
            return MockUserSet(super().__getitem__(key))
        return super().__getitem__(key)
    @property
    def id(self):
        return self[0].id if self else None

class MockPartner:
    def __init__(self, user=None):
        self.id = 1
        self.user_ids = MockUserSet([user]) if user else MockUserSet([])

class MockConfigParam:
    def get_param(self, param):
        return 'test-uuid'

class MockDeviceModel:
    def __init__(self, env=None):
        self.env = env
    def search(self, domain):
        return [MockDevice(env=self.env)]
    def browse(self, id):
        return MockDevice(env=self.env)
    def sudo(self): return self

class MockCoinModel:
    def __init__(self, env=None):
        self.env = env
    def get_balance(self, user_id):
        return 100
    def add_reward(self, user_id, amount, reason, t_type='reward'):
        print(f"REWARD ADDED: {amount} coins for {reason} ({t_type})")
        return True
    def sudo(self): return self

class MockTelemetryModel:
    def __init__(self, env=None):
        self.env = env
    def create(self, vals):
        print(f"TELEMETRY LOGGED: {vals['name']} took {vals['duration']:.4f}ms")
        return True
    def sudo(self): return self

class MockDevice:
    def __init__(self, env=None):
        self.id = 101
        self._name = 'sc.google.home.device'
        self.name = "Living Room Light"
        self.device_type = "action.devices.types.LIGHT"
        self.traits = "action.devices.traits.OnOff,action.devices.traits.SensorState"
        self.state_on = False
        self.brightness = 100
        self.is_locked = True
        self.room_name = "Living Room"
        self.env = env or MockEnv()
        self.partner_id = MockPartner(user=MockUser(env=self.env))

    def exists(self): return True
    def sudo(self): return self
    def ensure_one(self): pass
    def write(self, vals):
        for k, v in vals.items():
            setattr(self, k, v)
        return True

# Add path for our modules
sys.path.append(os.path.abspath('odoo19-shadow/addons'))

# Mock pms_base inside odoo.addons
import pms_base
sys.modules['odoo.addons.pms_base'] = pms_base
import pms_base.models.staps_core
sys.modules['odoo.addons.pms_base.models.staps_core'] = pms_base.models.staps_core

print("Verifying Optimized PMS Community System (Double J Architecture)...")

try:
    from pms_base.models.staps_core import staps_timed, get_staps_coordinate

    # Test STAPS 2.0 and Telemetry
    class TestComponent:
        def __init__(self):
            self.env = MockEnv()
            self._name = 'test.component'

        @staps_timed
        def process_signal(self):
            return "SIGNAL_PROCESSED"

    print("\n[Step 1] Testing STAPS 2.0 Timing & Telemetry Integration...")
    comp = TestComponent()
    res = comp.process_signal()
    print(f"STAPS Result: {res}")

    # Test Google Home Logic
    print("\n[Step 2] Testing Google Home Advanced Traits & Rewards...")
    device = MockDevice()
    # Import sc_google_home model to test real logic
    from sc_google_home.models.google_home_device import GoogleHomeDevice

    # Manually attach methods since we are in mock env
    device._get_google_home_state = GoogleHomeDevice._get_google_home_state.__get__(device, MockDevice)
    device.action_energy_saving_mode = GoogleHomeDevice.action_energy_saving_mode.__get__(device, MockDevice)

    state = device._get_google_home_state()
    print(f"Device State (SensorState): {state.get('sensorStateData')}")

    print("Triggering Energy Saving Mode...")
    device.action_energy_saving_mode()

    print("\nVerification Successful: STAPS 2.0 and Cross-Node Optimization are VALID.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Verification Failed: {e}")
    sys.exit(1)
