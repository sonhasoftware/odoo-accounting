from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccBaoCaoMenu(models.Model):
    _name = 'acc.bao.cao.menu'
    _description = 'Cấu hình menu báo cáo'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'sequence, name, id'

    name = fields.Char(string='Tên menu', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    parent_id = fields.Many2one('acc.bao.cao.menu', string='Menu cha', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('acc.bao.cao.menu', 'parent_id', string='Menu con')
    report_id = fields.Many2one('acc.bao.cao', string='Báo cáo')
    report_type = fields.Selection(
        [('summary', 'Báo cáo tổng hợp'), ('detail', 'Báo cáo chi tiết')],
        string='Loại báo cáo',
        default='summary',
        required=True,
    )
    menu_id = fields.Many2one('ir.ui.menu', string='Menu Odoo', readonly=True, copy=False, ondelete='set null')
    active = fields.Boolean(default=True)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Không được cấu hình menu báo cáo cha/con vòng lặp.'))

    def _get_report_root_menu(self):
        return self.env.ref('sonha_ke_toan.menu_bao_cao')

    def _get_report_action(self):
        self.ensure_one()
        action_xmlid = 'sonha_ke_toan.bao_cao_dt_action' if self.report_type == 'detail' else 'sonha_ke_toan.bao_cao_action'
        action = self.env.ref(action_xmlid)
        return 'ir.actions.act_window,%s' % action.id

    def _get_menu_values(self):
        self.ensure_one()
        parent_menu = self.parent_id.menu_id if self.parent_id else self._get_report_root_menu()
        values = {
            'name': self.name,
            'parent_id': parent_menu.id,
            'sequence': self.sequence,
            'active': self.active,
        }
        if self.report_id:
            values.update({
                'action': self._get_report_action(),
                'context': "{'default_bao_cao': %s}" % self.report_id.id,
            })
        else:
            values.update({
                'action': False,
                'context': False,
            })
        return values

    def _sync_menu(self):
        for record in self.sorted(lambda item: len(item.parent_path or '')):
            if record.parent_id and not record.parent_id.menu_id:
                record.parent_id._sync_menu()
            values = record._get_menu_values()
            if record.menu_id:
                record.menu_id.write(values)
            else:
                record.menu_id = self.env['ir.ui.menu'].create(values)
            record.child_ids._sync_menu()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_menu()
        return records

    def write(self, vals):
        result = super().write(vals)
        self._sync_menu()
        return result

    def unlink(self):
        menus = self.mapped('menu_id')
        result = super().unlink()
        menus.unlink()
        return result
