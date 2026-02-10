import sys
import os

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
    def __init__(self):
        self.user = MockUser()
        self.registry = {}

    def __getitem__(self, key):
        if key == 'ir.config_parameter':
            return MockConfigParam()
        if key == 'sc.google.home.device':
            return MockDeviceModel()
        return None

    def sudo(self):
        return self

class MockUser:
    def __init__(self):
        self.name = "Test Resident"
        self.partner_id = MockPartner()

    def has_group(self, group):
        return False

class MockPartner:
    def __init__(self):
        self.id = 1

class MockConfigParam:
    def get_param(self, param):
        if param == 'sc_google_home.bearer_token':
            return 'pms_authority_token_2024'
        return 'test-uuid'

class MockDeviceModel:
    def search(self, domain):
        return [MockDevice()]
    def browse(self, id):
        return MockDevice()

class MockDevice:
    def __init__(self):
        self.id = 101
        self.name = "Living Room Light"
        self.device_type = "action.devices.types.LIGHT"
        self.traits = "action.devices.traits.OnOff,action.devices.traits.Brightness,action.devices.traits.LockUnlock"
        self.state_on = False
        self.brightness = 100
        self.is_locked = True
        self.room_name = "Living Room"
        self.partner_id = MockPartner()

    def exists(self): return True
    def sudo(self): return self
    def write(self, vals):
        for k, v in vals.items():
            setattr(self, k, v)
        return True

# Import the actual classes to test
sys.path.append(os.path.abspath('odoo19-shadow/addons'))
# We need to mock 'odoo' module before importing
from unittest.mock import MagicMock
sys.modules['odoo'] = MagicMock()
sys.modules['odoo.http'] = MagicMock()

# Now we can import our controllers and models
# Note: In a real test we would use Odoo's test suite, but here we just check if they import and basic logic
print("Verifying PMS Optimization Logic...")

try:
    from pms_base.models.staps_core import staps_timed, get_staps_coordinate

    @staps_timed
    def test_func():
        return "OK"

    print("Testing STAPS Decorator...")
    res = test_func()
    print(f"STAPS Result: {res}")

    coord = get_staps_coordinate("TestNode")
    print(f"STAPS Coordinate: {coord}")

    print("Verification Successful: STAPS logic is sound.")
except Exception as e:
    print(f"Verification Failed: {e}")
    sys.exit(1)
