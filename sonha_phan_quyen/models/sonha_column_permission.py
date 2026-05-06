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

    def _apply_column_permissions_to_arch(self, arch_text, view_type):
        # Yêu cầu nghiệp vụ: bỏ cơ chế ẩn/hiện cột theo từng người dùng.
        # Giữ model cấu hình để không làm hỏng dữ liệu cũ, nhưng không áp dụng vào view.
        return arch_text

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if result.get('arch'):
            result['arch'] = self._apply_column_permissions_to_arch(result['arch'], view_type)
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if result.get('arch'):
            result['arch'] = self._apply_column_permissions_to_arch(result['arch'], view_type)
        return result
