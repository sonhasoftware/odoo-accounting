from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, registry):
    """Chạy khi cài module: tạo các bản ghi phân quyền (mặc định can_read=False)."""
    env = Environment(cr, SUPERUSER_ID, {})
    # module mặc định cần quét là 'ke_toan_son_ha'
    try:
        env['sonha.phan.quyen'].sudo().sync_permissions(module_name='sonha_ke_toan')
    except Exception:
        # nếu model chưa sẵn (trong trường hợp khác), bỏ qua lỗi để install không fail
        pass
