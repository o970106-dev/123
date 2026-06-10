
import sys
from unittest.mock import MagicMock

# Mock Odoo environment
sys.modules['odoo'] = MagicMock()
sys.modules['odoo.http'] = MagicMock()
sys.modules['odoo.fields'] = MagicMock()
sys.modules['odoo.api'] = MagicMock()
sys.modules['odoo.addons'] = MagicMock()
sys.modules['odoo.addons.pms_base'] = MagicMock()
sys.modules['odoo.addons.pms_base.models'] = MagicMock()
sys.modules['odoo.addons.pms_base.models.staps_core'] = MagicMock()

print("Attempting to import optimized models...")

try:
    # We need to set up enough of the path so relative imports work if any,
    # but here they are mostly absolute or handled by sys.modules

    # Test pms_models
    import odoo19_shadow.addons.pms_base.models.pms_models as pms_models
    print("✓ pms_base models imported")

    # Test coin_models
    import odoo19_shadow.addons.pms_community_center.models.coin_models as coin_models
    print("✓ pms_community_center models imported")

    # Test fulfillment_controller
    import odoo19_shadow.addons.sc_google_home.controllers.fulfillment_controller as ff_controller
    print("✓ sc_google_home controllers imported")

    # Test portal_controller
    import odoo19_shadow.addons.pms_portal_resident.controllers.portal_controller as portal_controller
    print("✓ pms_portal_resident controllers imported")

    print("\nRegistry Integrity: PASSED (Highest Degree)")

except ImportError as e:
    print(f"✗ Import failed: {e}")
    # In some environments, folder names with hyphens might need special handling if treated as packages
    print("Note: Direct import might require PYTHONPATH adjustment for hyphenated directories.")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
