from odoo import models, fields

class WuchangBankClearance(models.Model):
    _name = 'wuchang.bank.clearance'
    _description = 'Wuchang Bank Clearance'

    name = fields.Char(string='Reference', required=True)
    amount = fields.Float(string='Amount')
    date = fields.Date(string='Clearance Date', default=fields.Date.context_today)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')
