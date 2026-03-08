from odoo import models, fields, api

class SCGoogleHomeDevice(models.Model):
    _inherit = 'pms.device'

    google_device_id = fields.Char(string='Google Device ID', compute='_compute_google_id')

    def _compute_google_id(self):
        for rec in self:
            rec.google_device_id = f"pms_dev_{rec.id}"

    def get_google_traits(self):
        traits = ['action.devices.traits.OnOff']
        if self.device_type == 'lock':
            traits.append('action.devices.traits.LockUnlock')
        # Add SensorState for Happiness Coins reporting
        traits.append('action.devices.traits.SensorState')
        return traits

    def get_google_capabilities(self):
        return {
            'action.devices.traits.SensorState': {
                'numericCapabilities': [
                    {'name': 'Happiness Coins', 'unit': 'COIN'}
                ]
            }
        }
