from odoo import models, fields

class WuchangBankClearance(models.Model):
    _name = 'wuchang.bank.clearance'
    _description = 'Wuchang Bank Clearance'

    name = fields.Char('Name', required=True)
