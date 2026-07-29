from odoo import models, fields

class PMSTelemetry(models.Model):
    _name = 'pms.telemetry'
    _description = 'STAPS High-Precision Telemetry'
    _order = 'timestamp desc'

    name = fields.Char(string='Action Name', required=True)
    duration = fields.Float(string='Duration (ms)', digits=(16, 6))
    staps_coordinate = fields.Char(string='STAPS Coordinate', index=True)
    source_node = fields.Char(string='Source Node')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
