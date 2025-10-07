from odoo import models
import logging

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    # def load_menus(self, debug=False):
    #     """
    #     Chỉ hiển thị các menu con trong cây 'sonha_ke_toan.menu_sonha_accounting'
    #     nếu người dùng có quyền XEM_DM = True trong sonha.phan.quyen
    #     """
    #     try:
    #         res = super().load_menus(debug=debug)
    #         user = self.env.user
    #
    #         # --- Lấy danh sách model user được phép XEM ---
    #         allowed_models = self.env["sonha.phan.quyen"].sudo().search([
    #             ("NGUOI_DUNG", "=", user.id),
    #             ("XEM_DM", "=", True),
    #         ]).mapped("TEN_BANG") or []
    #         allowed_set = {str(m).lower() for m in allowed_models}
    #         _logger.info(">>> [MenuFilter] User=%s allowed_models=%s", user.login, allowed_set)
    #
    #         # --- Hàm đệ quy lọc menu ---
    #         def filter_menu(menu_dict):
    #             menu = dict(menu_dict)
    #             action_model = None
    #
    #             # Nếu có action -> kiểm tra model
    #             if menu.get("action"):
    #                 try:
    #                     action_id = int(str(menu["action"]).split(",")[-1])
    #                     action = self.env["ir.actions.act_window"].browse(action_id)
    #                     action_model = action.res_model if action.exists() else None
    #                 except Exception:
    #                     action_model = None
    #
    #                 # Nếu không được phép xem model này -> ẩn menu
    #                 if not action_model or str(action_model).lower() not in allowed_set:
    #                     _logger.debug("✗ Hide menu '%s' (model=%s not allowed)", menu.get("name"), action_model)
    #                     return None
    #
    #             # Đệ quy children
    #             children = menu.get("children") or []
    #             menu["children"] = [m for m in map(filter_menu, children) if m]
    #
    #             # Nếu menu không có action và không còn con → bỏ (ẩn nhóm trống)
    #             if not menu.get("action") and not menu["children"]:
    #                 _logger.debug("✗ Hide empty group '%s'", menu.get("name"))
    #                 return None
    #
    #             _logger.debug("✓ Keep menu '%s' (model=%s)", menu.get("name"), action_model)
    #             return menu
    #
    #         # --- Chỉ áp dụng cho cây con của sonha_ke_toan ---
    #         target_xmlid = "sonha_ke_toan.menu_sonha_accounting"
    #         try:
    #             target_menu = self.env.ref(target_xmlid)
    #             target_menu_id = target_menu.id
    #         except Exception:
    #             target_menu_id = None
    #
    #         if target_menu_id:
    #             def traverse_and_filter(nodes):
    #                 for node in nodes:
    #                     if node.get("id") == target_menu_id:
    #                         _logger.info(">>> Filtering subtree of menu_sonha_accounting (id=%s)", target_menu_id)
    #                         node["children"] = [m for m in map(filter_menu, node.get("children", [])) if m]
    #                     else:
    #                         traverse_and_filter(node.get("children", []) or [])
    #             traverse_and_filter(res.get("children", []) or [])
    #
    #         return res
    #
    #     except Exception as e:33333333333333333333333
    #         _logger.exception("!!! Error in custom load_menus: %s", e)
    #         return super().load_menus(debug=debug)
