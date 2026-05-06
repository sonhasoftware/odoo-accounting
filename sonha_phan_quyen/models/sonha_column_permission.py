from lxml import etree

from odoo import api, fields, models


class SonhaColumnPermission(models.Model):
    _name = 'sonha.column.permission'
    _description = 'Phân quyền ẩn/hiện cột'
    _rec_name = 'display_name'
    _order = 'user_id, model_id, field_name'

    user_id = fields.Many2one('res.users', string='Người dùng', required=True, ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Tên kỹ thuật model', store=True)
    field_name = fields.Char(string='Tên kỹ thuật cột', required=True)
    field_id = fields.Many2one('ir.model.fields', string='Trường', required=True, ondelete='cascade')
    is_visible = fields.Boolean(string='Hiển thị', default=True)
    active = fields.Boolean(default=True)
    display_name = fields.Char(compute='_compute_display_name', store=False)

    _sql_constraints = [
        (
            'unique_user_model_field',
            'unique(user_id, model_id, field_name)',
            'Mỗi user chỉ có một dòng phân quyền cho một cột của một model.',
        )
    ]

    @api.depends('user_id', 'model_id', 'field_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.user_id.name or ''} - {rec.model_name or ''}.{rec.field_name or ''}"

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_id = False

    @api.onchange('field_id')
    def _onchange_field_id(self):
        if self.field_id:
            self.field_name = self.field_id.name

    @api.model
    def create(self, vals):
        if vals.get('field_id') and not vals.get('field_name'):
            vals['field_name'] = self.env['ir.model.fields'].browse(vals['field_id']).name
        return super().create(vals)

    def write(self, vals):
        if vals.get('field_id') and not vals.get('field_name'):
            vals['field_name'] = self.env['ir.model.fields'].browse(vals['field_id']).name
        return super().write(vals)


class BaseColumnPermissionMixin(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type not in ('tree', 'form') or not result.get('arch') or self.env.su:
            return result

        target_models = {self._name}
        if view_type == 'form':
            arch_for_models = etree.fromstring(result['arch'])
            for node in arch_for_models.xpath('//field[@name]/tree'):
                parent_field = node.getparent()
                parent_field_name = parent_field.get('name') if parent_field is not None else False
                field_def = self._fields.get(parent_field_name)
                comodel_name = getattr(field_def, 'comodel_name', False)
                if comodel_name:
                    target_models.add(comodel_name)

        hidden_columns = self.env['sonha.column.permission'].sudo().search([
            ('user_id', '=', self.env.user.id),
            ('model_name', 'in', list(target_models)),
            ('is_visible', '=', False),
            ('active', '=', True),
        ])

        if not hidden_columns:
            return result

        hidden_fields_by_model = {}
        for rec in hidden_columns:
            hidden_fields_by_model.setdefault(rec.model_name, set()).add(rec.field_name)

        arch = etree.fromstring(result['arch'])
        if view_type == 'tree':
            hidden_field_names = hidden_fields_by_model.get(self._name, set())
            for field_node in arch.xpath('//tree//field[@name]'):
                if field_node.get('name') in hidden_field_names:
                    field_node.set('optional', 'hide')
        else:
            # Ẩn field của model chính ngay trên form (không chỉ optional ở tree)
            main_hidden_field_names = hidden_fields_by_model.get(self._name, set())
            if main_hidden_field_names:
                for field_node in arch.xpath('//form//field[@name]'):
                    if field_node.get('name') in main_hidden_field_names:
                        field_node.set('invisible', '1')

            # Ẩn field trong các one2many tree nằm trong form
            for tree_node in arch.xpath('//field[@name]/tree'):
                parent_field = tree_node.getparent()
                parent_field_name = parent_field.get('name') if parent_field is not None else False
                field_def = self._fields.get(parent_field_name)
                comodel_name = getattr(field_def, 'comodel_name', False)
                hidden_field_names = hidden_fields_by_model.get(comodel_name, set())
                if not hidden_field_names:
                    continue
                for field_node in tree_node.xpath('.//field[@name]'):
                    if field_node.get('name') in hidden_field_names:
                        field_node.set('optional', 'hide')

        result['arch'] = etree.tostring(arch, encoding='unicode')
        return result
