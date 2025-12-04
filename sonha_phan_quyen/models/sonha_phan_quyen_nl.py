from odoo import api, fields, models


class SonhaPhanQuyenNL(models.Model):
    _name = 'sonha.phan.quyen.nl'

    MENU = fields.Many2one('ir.ui.menu', string="ID MENU", store=True)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True)

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