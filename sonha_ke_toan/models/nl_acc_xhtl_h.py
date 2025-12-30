import datetime

from odoo import api, fields, models, exceptions, _, tools
import datetime
import logging
import re
import json

_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError

class NLAccApXhtlH(models.Model):
    _name = 'nl.acc.ap.xhtl.h'
    _order = 'NGAY_CT DESC'
    _rec_name = 'CHUNG_TU'

    NGAY_CT = fields.Date(string="Ngày CT", store=True, default=lambda self: datetime.date.today())
    CHUNG_TU = fields.Char(string="Chứng từ", store=True, readonly=True, size=30)
    CTGS = fields.Char(string="CTGS", store=True, size=30)
    SO_HD = fields.Char(string="Số HĐ", store=True, size=10)
    SERI_HD = fields.Char(string="Seri HĐ", store=True, size=10)
    NGAY_HD = fields.Date(string="Ngày HĐ", store=True)
    MAU_SO = fields.Char(string="Mẫu số", store=True, size=10)
    PT_THUE = fields.Many2one('acc.thue', string="% Thuế", store=True)
    ONG_BA = fields.Char(string="Ông bà", store=True, size=60)
    GHI_CHU = fields.Char(string="Ghi chú", store=True, default="Phiếu báo nợ", size=200)

    KHACH_HANG = fields.Many2one('acc.khach.hang', string="Khách hàng", store=True)
    KH_THUE = fields.Char(string="KH Thuế", store=True, size=150)
    MS_THUE = fields.Char(string="Mã số Thuế", store=True, size=20)
    DC_THUE = fields.Char(string="Địa chỉ Thuế", store=True, size=200)

    BO_PHAN = fields.Many2one('acc.bo.phan', string="Bộ phận", store=True)

    # Liên kết đến bảng vụ việc (hợp đồng)
    VVIEC = fields.Many2one('acc.vviec', string="Vụ việc", store=True)

    # Liên kết đến bảng kho
    KHO = fields.Many2one('acc.kho', string="Kho", store=True)

    # Khoản mục (nếu là bảng riêng thì có thể Many2one)
    KHOAN_MUC = fields.Many2one('acc.khoan.muc', string="Khoản mục", store=True)

    TIEN_TE = fields.Many2one('acc.tien.te', string="Tiền tệ", store=True)
    TY_GIA = fields.Float(string="Tỷ giá", store=True, default=1)

    # Liên kết đến bảng tài khoản
    MA_TK0_ID = fields.Many2one('acc.tai.khoan', string="Nợ", store=True)
    MA_TK0 = fields.Char(related='MA_TK0_ID.MA', string="Nợ", store=True)
    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True)
    MA_TK1 = fields.Char(related='MA_TK1_ID.MA', string="Có", store=True)

    # Liên kết đến bảng đơn vị cơ sở (DVCS)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)

    # Liên kết đến bảng chi nhánh
    CHI_NHANH = fields.Many2one('acc.chi.nhanh', string="Chi nhánh", store=True)

    ACC_SP_D = fields.One2many(
        comodel_name="nl.acc.ap.bn.d",
        inverse_name="ACC_AP_H",
        string="Bảng chi tiết",
        store=True
    )
    MENU_ID = fields.Many2one('ir.ui.menu', string="MENU", store=True)

    DG_THEO_TIEN = fields.Boolean("DG theo tiền", store=False)
    TOTAL_VAT = fields.Char("Tổng tiền, Tổng VAT, tổng SL", store=False, compute="_get_total_vat_sl_tien")
    KHACH_HANGC = fields.Many2one('acc.khach.hang', string="KH có", store=True)
    KHOC = fields.Many2one('acc.kho', string="Kho nhận", store=True)
    TINH = fields.Many2one('acc.tinh', string="Vùng", store=True)
    NGUON = fields.Many2one('acc.nguon', string="HTV Chuyển", store=True)
    LOAIDL = fields.Many2one('acc.loaidl', string="Loại DL", store=True)

    @api.onchange('ACC_SP_D', 'ACC_SP_D.PS_NO1', 'ACC_SP_D.VAT', 'ACC_SP_D.SO_LUONG')
    def _get_total_vat_sl_tien(self):
        for r in self:
            lines = r.ACC_SP_D
            r.TOTAL_VAT = (
                f"Tổng tiền:{sum(lines.mapped('PS_NO1'))}, "
                f"VAT:{sum(lines.mapped('VAT'))}, "
                f"Tổng SL:{sum(lines.mapped('SO_LUONG'))}"
            )

    # @api.model
    # def _get_domain_tai_khoan(self):
    #     """
    #     Domain động cho field MA_TK0_ID dựa trên dữ liệu trả về từ function PostgreSQL.
    #     """
    #     company_id = self.env.company.id
    #
    #     query = "SELECT * FROM public.fn_acc_tai_khoan_nl(%s)"
    #     self.env.cr.execute(query, (company_id,))
    #     rows = self.env.cr.fetchall()
    #
    #     ids = [r[0] for r in rows if r and r[0]]
    #     if not ids:
    #         return [('id', '=', 0)]
    #
    #     return [('id', 'in', ids)]

    def default_get(self, fields_list):
        res = super(NLAccApBnH, self).default_get(fields_list)
        # Tìm phân quyền của user hiện tại
        permission = self.env['sonha.phan.quyen.nl'].sudo().search([
            ('MENU', '=', 396),
        ], limit=1)
        dl = self.env['acc.loaidl'].sudo().search([('id', '=', 5)])

        if permission:
            res.update({
                'BO_PHAN': permission.BO_PHAN.id or None,
                'KHO': permission.KHO.id or None,
                'KHOAN_MUC': permission.KHOAN_MUC.id or None,
                'VVIEC': permission.VVIEC.id or None,
                'CHI_NHANH': permission.CHI_NHANH.id or None,
                'DVCS': permission.DVCS.id or None,
                'TIEN_TE': permission.TIEN_TE.id or None,
                'MENU_ID': permission.MENU.id or None,
                'MA_TK1_ID': permission.MA_TK1_ID.id or None,
                'LOAIDL': permission.LOAI_DL.id or dl.id,
            })

        return res