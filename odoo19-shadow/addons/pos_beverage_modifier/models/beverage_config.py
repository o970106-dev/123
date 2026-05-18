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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    beverage_config_ids = fields.One2many(
        'pos.beverage.config', 'product_tmpl_id', string='Beverage Settings'
    )
    beverage_config_count = fields.Integer(
        string='Beverage Settings Count', compute='_compute_beverage_config_count'
    )

    def _compute_beverage_config_count(self):
        for rec in self:
            rec.beverage_config_count = self.env['pos.beverage.config'].search_count(
                [('product_tmpl_id', '=', rec.id)]
            )

    def action_open_beverage_configs(self):
        self.ensure_one()
        action = self.env.ref('pos_beverage_modifier.action_pos_beverage_config').read()[0]
        action['domain'] = [('product_tmpl_id', '=', self.id)]
        action['context'] = {'default_product_tmpl_id': self.id}
        return action


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_pos_beverage_config(self, params):
        return self.env['pos.beverage.config'].search_read(params['domain'], params['fields'])

    def _get_pos_ui_pos_beverage_config_line(self, params):
        return self.env['pos.beverage.config.line'].search_read(params['domain'], params['fields'])

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result += ['pos.beverage.config', 'pos.beverage.config.line']
        return result

    def _loader_params_pos_beverage_config(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['name', 'product_tmpl_id', 'pos_category_id', 'show_popup', 'line_ids'],
            },
        }

    def _loader_params_pos_beverage_config_line(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['config_id', 'attribute_type', 'name', 'selected', 'price'],
            },
        }
