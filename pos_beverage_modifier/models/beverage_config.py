from odoo import models, fields, api


class PosBeverageConfig(models.Model):
    _name = 'pos.beverage.config'
    _description = 'POS Beverage Configuration'

    name = fields.Char(string='Name', required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True)
    pos_category_id = fields.Many2one('pos.category', string='POS Category')
    show_popup = fields.Boolean(string='Show Modifier Popup', default=True)
    line_ids = fields.One2many('pos.beverage.config.line', 'config_id', string='Customization Items')

    def _apply_to_product_template(self):
        """Propagate selected POS category to the linked product template upon save."""
        for rec in self:
            if rec.product_tmpl_id and rec.pos_category_id:
                # Guard for environments where POS module may not be installed
                if 'pos_categ_id' in rec.product_tmpl_id._fields:
                    rec.product_tmpl_id.pos_categ_id = rec.pos_category_id.id

    @api.model
    def create(self, vals):
        res = super(PosBeverageConfig, self).create(vals)
        res._apply_to_product_template()
        return res

    def write(self, vals):
        res = super(PosBeverageConfig, self).write(vals)
        self._apply_to_product_template()
        return res


class PosBeverageConfigLine(models.Model):
    _name = 'pos.beverage.config.line'
    _description = 'POS Beverage Customization Item'

    config_id = fields.Many2one('pos.beverage.config', string='Configuration', required=True, ondelete='cascade')
    attribute_type = fields.Selection([
        ('sweetness', '甜度'),
        ('temperature', '溫度'),
        ('size', '尺寸'),
        ('other', '其他'),
    ], string='Type', default='other')
    name = fields.Char(string='Item Name', required=True)
    selected = fields.Boolean(string='Selected', default=False)
    price = fields.Float(string='Price Extra', default=0.0)
