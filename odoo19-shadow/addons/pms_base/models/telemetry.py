from odoo import models, fields

class PMSTelemetry(models.Model):
    _name = 'pms.telemetry'
    _description = 'PMS High Precision Telemetry'
    _order = 'create_date desc'

    name = fields.Char(string='Action Name')
    duration = fields.Float(string='Duration (ms)')
    coordinate = fields.Char(string='STAPS Coordinate')
    node_info = fields.Char(string='Source Node')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
