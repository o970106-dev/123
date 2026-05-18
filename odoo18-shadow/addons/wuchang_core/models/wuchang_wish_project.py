from odoo import models, fields

class WuchangWishProject(models.Model):
    _name = 'wuchang.wish.project'
    _description = 'Wuchang Wish Project'

    name = fields.Char('Name', required=True)
