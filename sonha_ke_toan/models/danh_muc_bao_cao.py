from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccBaoCao(models.Model):
    _name = 'acc.bao.cao'
    _rec_name = 'TEN'

    MA = fields.Char(string="Mã", store=True)
    TEN = fields.Char(string="Tên", store=True)
    BO_PHAN = fields.Many2one('acc.bo.phan', string="Bộ phận", store=True)
    KHOAN_MUC = fields.Many2one('acc.khoan.muc', string="Khoản mục", store=True)
    HANG_HOA = fields.Many2one('acc.hang.hoa', string="Hàng hóa", store=True)
    KHO = fields.Many2one('acc.kho', string="Kho", store=True)
    TSCD = fields.Many2one('acc.tscd', string="TSCD", store=True)
    VVIEC = fields.Many2one('acc.vviec', string="VVIEC", store=True)
    KHACH_HANG = fields.Many2one('acc.khach.hang', string="Khách hàng", store=True)
    FN_BAO_CAO = fields.Char(string="function báo cáo", store=True)
    TU_TK = fields.Char(string="Từ TK", store=True)
    DK_DAU = fields.Char(string="DK đầu báo cáo", store=True)
    TINH_SAU = fields.Char(string="Tính trước khi hiển thị báo cáo", store=True)
    DK_SAU = fields.Char(string="DK sau báo cáo", store=True)
    DK_GOI_BC = fields.Char(string="DK để link báo cáo", store=True)
    FN_GOI_BC = fields.Char(string="Function gọi báo cáo", store=True)
