from odoo import api, fields, models


class SonhaPhanQuyen(models.Model):
    _name = 'sonha.phan.quyen'

    NGUOI_DUNG_ID = fields.Many2one('sonha.user', string="Người dùng", store=True)
    NGUOI_DUNG = fields.Integer(string="Người dùng (Base)", store=True)
    SONHA_USER = fields.Integer(string="Người dùng Sơn Hà", store=True)
    TEN_BANG = fields.Many2one('ir.model', string="Mã Bảng", store=True)
    # đây là mã bảng model
    MA_BANG = fields.Char(related='TEN_BANG.model', string="Tên Bảng", store=True)
    # đây là tên bảng
    MENU = fields.Many2one('ir.ui.menu', string="ID MENU", store=True)
    XEM_DM = fields.Boolean(string="Xem DM", default=False, store=True)
    THEM_DM = fields.Boolean(string="Thêm DM", default=False, store=True)
    SUA_DM = fields.Boolean(string="Sửa DM", default=False, store=True)
    XOA_DM = fields.Boolean(string="Xóa DM", default=False, store=True)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True)

    THEM_DL = fields.Boolean(string="Thêm mới DL", default=False, store=True)
    XEM_DL = fields.Many2many('sonha.user', 'xem_dl_rel', 'xem_dl_phan_quyen', 'xem_dl_id',
                                 string="Xem DL của User", store=True)
    SUA_DL = fields.Many2many('sonha.user', 'sua_dl_rel', 'sua_dl_phan_quyen', 'sua_dl_id',
                              string="Sửa DL của User", store=True)
    ACTIVE = fields.Boolean(string="ACTIVE", default=False, store=True)

    BO_PHAN = fields.Many2one('acc.bo.phan', string="Bộ phận", store=True)
    KHO = fields.Many2one('acc.kho', string="Kho", store=True)
    KHOAN_MUC = fields.Many2one('acc.khoan.muc', string="Khoản mục", store=True)
    VVIEC = fields.Many2one('acc.vviec', string="Vụ việc", store=True)
    LOAI_NX = fields.Many2one('acc.loai.nx', string="Phân xưởng", store=True)
    LOAI_DL = fields.Many2one('acc.loaidl', string="Loại DL", store=True)
    CHI_NHANH = fields.Many2one('acc.chi.nhanh', string="Chi nhánh", store=True)

    MA_TK0_ID = fields.Many2one('acc.tai.khoan', string="Nợ", store=True)
    MA_TK0 = fields.Char(related='MA_TK0_ID.MA', string="Nợ", store=True)

    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True)
    MA_TK1 = fields.Char(related='MA_TK1_ID.MA', string="Có", store=True)

    TIEN_TE = fields.Many2one('acc.tien.te', string="DVTT", store=True)
    KT_SL = fields.Boolean(string="KT số lượng", store=True)
    GIA_MUA = fields.Boolean(string="Giá mua theo BG", store=True)
    GIA_BAN = fields.Boolean(string="Giá bán theo BG", store=True)
    MOT_VE = fields.Boolean(string="Một vế", store=True)
    KHONG_TINH_GV = fields.Boolean(string="Không tính GV", store=True)
    CT_KHONG_TD = fields.Boolean(string="CT không tự động", store=True)
    PT_VAT = fields.Char(string="%VAT", store=True)
    CHUNG_TU = fields.Char(string="Chứng từ", store=True)

    # _sql_constraints = [
    #     ('unique_user_menu', 'unique(user_id, menu_id)', 'Mỗi người dùng chỉ có 1 bản ghi phân quyền cho 1 menu.')
    # ]

    # @api.model
    # def sync_permissions(self, module_name='sonha_ke_toan'):
    #     """
    #     Tạo các bản ghi ke.toan.permission cho mọi ir.ui.menu của module module_name,
    #     nếu menu đó chưa có bản ghi phân quyền nào.
    #     Mặc định can_read/can_create/can_write = False.
    #     """
    #     IrModelData = self.env['ir.model.data'].sudo()
    #     # Lấy ir.model.data records cho ir.ui.menu thuộc module_name
    #     data_recs = IrModelData.search([('model', '=', 'ir.ui.menu'), ('module', '=', module_name)])
    #     menu_ids = data_recs.mapped('res_id')
    #     if not menu_ids:
    #         return False
    #
    #     Menu = self.env['ir.ui.menu'].sudo()
    #     existing_menu_ids = self.search([('MENU', 'in', menu_ids)]).mapped('MENU').ids
    #     to_create = []
    #     for mid in menu_ids:
    #         if mid in existing_menu_ids:
    #             continue
    #         menu = Menu.browse(mid)
    #         # cố gắng lấy model code từ action nếu có (an toàn: kiểm tra attribute)
    #         action = False
    #         if hasattr(menu, 'action') and menu.action:
    #             action = menu.action
    #         elif hasattr(menu, 'action_id') and menu.action_id:
    #             action = menu.action_id
    #         model_code = action and getattr(action, 'res_model', False) or False
    #
    #         to_create.append({
    #             'menu_id': mid,
    #             'model_name': menu.name,
    #             'model_code': model_code,
    #             'can_read': False,
    #             'can_create': False,
    #             'can_write': False,
    #         })
    #     if to_create:
    #         self.sudo().create(to_create)
    #     return True
