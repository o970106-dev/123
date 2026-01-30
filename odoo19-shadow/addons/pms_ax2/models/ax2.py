from odoo import models, fields

class PMSAX2(models.Model):
    _name = 'pms.ax2'
    _description = 'PMS Auxiliary Adapter Node 2'

    name = fields.Char(string='Node Name', default='AX2-Neural-Adapter')
    status = fields.Selection([('active', 'Active'), ('idle', 'Idle')], default='active')
