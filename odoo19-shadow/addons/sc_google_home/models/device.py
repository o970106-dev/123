from odoo import models, fields, api
from odoo.addons.pms_base.pms_coordination import timed_process

class GoogleHomeDevice(models.Model):
    _name = 'sc.google.home.device'
    _description = 'Google Home Integrated Device'

    name = fields.Char(string='Device Name', required=True)
    device_type = fields.Selection([
        ('LIGHT', 'Light'),
        ('OUTLET', 'Outlet'),
        ('THERMOSTAT', 'Thermostat'),
        ('FAN', 'Fan'),
        ('SCENE', 'Scene')
    ], string='Device Type', required=True, default='LIGHT')

    room_name = fields.Char(string='Room Name', help='Hint for Google Home room placement')
    partner_id = fields.Many2one('res.partner', string='Owner', help='Resident who owns this device')

    is_on = fields.Boolean(string='Power State', default=False)
    brightness = fields.Integer(string='Brightness', default=100)
    color_temp = fields.Integer(string='Color Temperature', default=2700)
    target_temp = fields.Float(string='Target Temperature', default=25.0)

    external_id = fields.Char(string='External ID', compute='_compute_external_id', store=True)

    @api.depends('name')
    def _compute_external_id(self):
        for record in self:
            # Simple unique ID for Google Home mapping
            record.external_id = f"device_{record.id}" if record.id else "temp"

    @timed_process("Device State Sync")
    def sync_to_cloud(self):
        """
        Example method using STAPS coordination to sync state.
        """
        # Logic to sync with external IoT cloud if necessary
        pass

    def action_toggle_power(self, state):
        self.write({'is_on': state})
        return True

    def action_set_brightness(self, level):
        self.write({'brightness': level, 'is_on': True if level > 0 else self.is_on})
        return True

    def action_set_temperature(self, temp):
        self.write({'target_temp': temp})
        return True

    def action_energy_saving_mode(self):
        """
        Advanced optimization: automated energy saving based on device type.
        """
        for record in self:
            if record.device_type == 'LIGHT':
                record.action_set_brightness(50)
            elif record.device_type == 'THERMOSTAT':
                record.action_set_temperature(26.0)
        return True
