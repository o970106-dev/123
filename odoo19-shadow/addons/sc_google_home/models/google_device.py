from odoo import models, fields

class SCGoogleHomeDevice(models.Model):
    _inherit = 'pms.device'

    # Redundant fields and methods removed.
    # Logic is now centralized in pms_base.models.pms_device.
