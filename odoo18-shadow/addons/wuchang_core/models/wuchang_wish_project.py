from odoo import models, fields

class WuchangWishProject(models.Model):
    _name = 'wuchang.wish.project'
    _description = 'Wuchang Wish Project'

    name = fields.Char(string='Project Name', required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
