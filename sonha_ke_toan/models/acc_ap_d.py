from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccApD(models.Model):
    _name = 'acc.ap.d'

    ACC_AP_H = fields.Many2one('acc.ap.h', string="ID Header", store=True)

    MA_TK0_ID = fields.Many2one('acc.tai.khoan', string="Nợ", store=True)
    MA_TK0 = fields.Char(related='MA_TK0_ID.MA', string="Nợ", store=True)

    HANG_HOA = fields.Many2one('acc.hang.hoa', string="Hàng hóa", store=True)

    SO_LUONG = fields.Float("SL", store=True)
    DON_GIA = fields.Float("Đơn giá", store=True)
    PS_NO1 = fields.Integer("Thành tiền", store=True)
    TIEN_NTE = fields.Float("Ngoại tệ", store=True)
    VAT = fields.Integer("Vat", store=True)

    # field theo header
    NGAY_CT = fields.Date(string="Ngày CT", store=True)
    CHUNG_TU = fields.Char(string="Chứng từ", store=True)
    SO_HD = fields.Char(string="Số HĐ", store=True)
    SERI_HD = fields.Char(string="Seri HĐ", store=True)
    NGAY_HD = fields.Date(string="Ngày HĐ", store=True)
    MAU_SO = fields.Char(string="Mẫu số", store=True)
    PT_THUE = fields.Char(string="% Thuế", store=True)
    ONG_BA = fields.Char(string="Ông bà", store=True)
    GHI_CHU = fields.Char(string="Ghi chú", store=True)

    KHACH_HANG = fields.Many2one('acc.khach.hang', string="Khách hàng", store=True)
    KH_THUE = fields.Char(string="KH Thuế", store=True)
    MS_THUE = fields.Char(string="Mã số Thuế", store=True)
    DC_THUE = fields.Char(string="Địa chỉ Thuế", store=True)

    BO_PHAN = fields.Many2one('acc.bo.phan', string="Bộ phận", store=True)

    # Liên kết đến bảng vụ việc (hợp đồng)
    VVIEC = fields.Many2one('acc.vviec', string="Vụ việc", store=True)

    # Liên kết đến bảng kho
    KHO = fields.Many2one('acc.kho', string="Kho", store=True)

    # Khoản mục (nếu là bảng riêng thì có thể Many2one)
    KHOAN_MUC = fields.Many2one('acc.khoan.muc', string="Khoản mục", store=True)

    TIEN_TE = fields.Many2one('acc.tien.te', string="Tiền tệ", store=True)
    TY_GIA = fields.Float(string="Tỷ giá", store=True)

    # Liên kết đến bảng tài khoản
    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True)
    MA_TK1 = fields.Char(related='MA_TK1_ID.MA', string="Có", store=True)

    # Liên kết đến bảng đơn vị cơ sở (DVCS)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)

    # Liên kết đến bảng chi nhánh
    CHI_NHANH = fields.Many2one('acc.chi.nhanh', string="Chi nhánh", store=True)

