import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class IrUiMenuInherit(models.Model):
    _inherit = 'ir.ui.menu'

    # @api.model
    # def load_menus(self, debug=False):
    #     """
    #     Lọc menu hiển thị dựa trên bảng phân quyền (model sonha.phan.quyen).
    #     Chỉ ẩn/kiểm soát các menu thuộc module 'sonha_ke_toan' — menu của module khác
    #     vẫn hiển thị bình thường. Admin (base.group_system) thấy tất cả.
    #     """
    #     res = super().load_menus(debug)
    #     user = self.env.user
    #
    #     # Admin thấy tất cả
    #     # if user.has_group('base.group_system'):
    #     #     return res
    #
    #     # --- Cấu hình: nếu tên model/module khác thì sửa ở đây ---
    #     perm_model_name = 'sonha.phan.quyen'  # model chứa quyền của bạn
    #     module_name = 'sonha_ke_toan'  # chỉ áp dụng filter cho module này
    #     # -------------------------------------------------------
    #
    #     # Nếu model phân quyền không tồn tại => trả nguyên (an toàn)
    #     if perm_model_name not in self.env:
    #         _logger.debug("Permission model %s not found, skip menu filtering", perm_model_name)
    #         return res
    #
    #     Perm = self.env[perm_model_name].sudo()
    #
    #     # Tự phát hiện tên các trường trong model phân quyền:
    #     # - trường many2one tới ir.ui.menu (vd: menu_id)
    #     # - trường many2one tới res.users (vd: user_id hoặc nguoi_dung)
    #     # - trường boolean thể hiện quyền xem (vd: can_read hoặc xem_dm)
    #     menu_field = None
    #     user_field = None
    #     read_field = None
    #
    #     for fname, f in Perm._fields.items():
    #         if not menu_field and f.type == 'many2one' and getattr(f, 'comodel_name', None) == 'ir.ui.menu':
    #             menu_field = fname
    #         if not user_field and f.type == 'many2one' and getattr(f, 'comodel_name', None) == 'sonha.user':
    #             user_field = fname
    #         if not read_field and f.type == 'boolean' and ('read' in fname.lower() or 'xem' in fname.lower()):
    #             read_field = fname
    #
    #     # fallback tên trường nếu không tìm được
    #     menu_field = menu_field or 'menu_id'
    #     user_field = user_field or 'user_id'
    #     read_field = read_field or 'can_read'
    #
    #     _logger.debug("Using permission fields: menu_field=%s, user_field=%s, read_field=%s",
    #                   menu_field, user_field, read_field)
    #
    #     # Tạo domain để lấy menu mà user được phép xem
    #     domain = [(user_field, '=', user.id), (read_field, '=', True)]
    #     try:
    #         perms = Perm.search(domain)
    #     except Exception as e:
    #         _logger.exception("Error searching permission records: %s", e)
    #         return res
    #
    #     # Lấy id các menu user được phép (an toàn lấy id bằng mapped)
    #     try:
    #         permitted_menu_ids = set(perms.mapped(f'{menu_field}.id'))
    #     except Exception:
    #         # fallback: lấy từng record
    #         permitted_menu_ids = set(getattr(rec, menu_field).id for rec in perms if getattr(rec, menu_field, False))
    #
    #     # Lấy danh sách menu thuộc module mục tiêu (sonha_ke_toan)
    #     imd = self.env['ir.model.data'].sudo()
    #     module_menu_ids = set(imd.search([('model', '=', 'ir.ui.menu'), ('module', '=', module_name)]).mapped('res_id'))
    #
    #     # Lấy tất cả menu hiện có
    #     Menu = self.env['ir.ui.menu'].sudo()
    #     all_menu_ids = set(Menu.search([]).ids)
    #
    #     # Quy tắc: những menu KHÔNG thuộc module sonha_ke_toan => luôn cho hiển thị.
    #     # Còn những menu thuộc module sonha_ke_toan => chỉ cho hiển thị nếu nằm trong permitted_menu_ids.
    #     allowed = (all_menu_ids - module_menu_ids) | permitted_menu_ids
    #
    #     # Mở rộng allowed để include ancestors (để cây menu hiển thị đúng)
    #     parents = Menu.browse(list(allowed)).mapped('parent_id')
    #     while parents:
    #         new_ids = set(parents.ids) - allowed
    #         if not new_ids:
    #             break
    #         allowed |= new_ids
    #         parents = parents.mapped('parent_id')
    #
    #     allowed_ids = allowed
    #
    #     # Hàm đệ quy cắt tỉa node: giữ node nếu id thuộc allowed hoặc node còn con hợp lệ
    #     def prune(node):
    #         kept_children = []
    #         for c in node.get('children', []):
    #             pr = prune(c)
    #             if pr:
    #                 kept_children.append(pr)
    #         node['children'] = kept_children
    #         if node.get('id') in allowed_ids or kept_children:
    #             return node
    #         return None
    #
    #     new_children = []
    #     for ch in res.get('children', []):
    #         pr = prune(ch)
    #         if pr:
    #             new_children.append(pr)
    #     res['children'] = new_children
    #     return res
