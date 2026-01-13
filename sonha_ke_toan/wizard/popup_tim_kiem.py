from odoo import models, fields, api
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta


class PopupTimKiem(models.TransientModel):
    _name = "popup.tim.kiem"
    _description = "Tm kiếm dữ liệu"

    start_date = fields.Date("Từ ngày", default=lambda self: self.default_from_date())
    end_date = fields.Date("Đến ngày", default=lambda self: self.default_to_date())

    tai_khoan = fields.Many2one('acc.tai.khoan', string="Tài khoản")
    chung_tu = fields.Char(string="Chứng từ")
    so_hd = fields.Char(string="Số HĐ")
    chi_nhanh = fields.Many2one('acc.chi.nhanh', string="Chi nhánh")
    khach_hang = fields.Many2one('acc.khach.hang', string="Khách hàng")
    hang_hoa = fields.Many2one('acc.hang.hoa', string="Hàng hóa")
    kho = fields.Many2one('acc.kho', string="Kho")
    tscd = fields.Many2one('acc.tscd', string="TSCĐ")
    bo_phan = fields.Many2one('acc.bo.phan', string="Bộ phận")
    khoan_muc = fields.Many2one('acc.khoan.muc', string="Khoản mục")
    vu_viec = fields.Many2one('acc.vviec', string="Vụ việc")
    thanh_pham = fields.Many2one('acc.san.pham', string="Thành phẩm")

    def default_get(self, fields_list):
        """
        Tự động lấy các giá trị mặc định từ bảng phân quyền acc.phan.quyen
        dựa theo người dùng đang đăng nhập.
        """
        user = self.env.user
        res = super(PopupTimKiem, self).default_get(fields_list)
        permission = self.env['save.data'].sudo().search([('user_id', '=', user.id),
                                                          ('type', '=', "tk")])

        res.update({
            "chung_tu": self.chung_tu or None,
            "so_hd": self.so_hd or None,
            "tai_khoan": permission.tai_khoan.id or None,
            "chi_nhanh": permission.chi_nhanh.id or None,
            "khach_hang": permission.khach_hang.id or None,
            "hang_hoa": permission.hang_hoa.id or None,
            "kho": permission.kho.id or None,
            "tscd": permission.tscd.id or None,
            "bo_phan": permission.bo_phan.id or None,
            "khoan_muc": permission.khoan_muc.id or None,
            "vu_viec": permission.vu_viec.id or None,
            "thanh_pham": permission.thanh_pham.id or None,
        })

        return res

    def default_from_date(self):
        now = datetime.today().date()
        from_date = now.replace(day=1)
        return from_date

    def default_to_date(self):
        now = datetime.today().date()
        to_date = (now.replace(day=1) + relativedelta(months=1)) - timedelta(days=1)
        return to_date

    def action_search(self):
        self.ensure_one()

        domain = []

        if self.tai_khoan:
            domain += [
                '|',
                ('MA_TK1_ID', '=', self.tai_khoan.id),
                ('MA_TK0_ID', '=', self.tai_khoan.id),
            ]

        if self.start_date:
            domain.append(('NGAY_CT', '>=', self.start_date))
        if self.end_date:
            domain.append(('NGAY_CT', '<=', self.end_date))

        if self.chung_tu:
            domain.append(('CHUNG_TU', 'ilike', self.chung_tu))

        if self.so_hd:
            domain.append(('SO_HD', 'ilike', self.SO_HD))

        if self.chi_nhanh:
            domain.append(('CHI_NHANH', '=', self.chi_nhanh.id))

        if self.khach_hang:
            domain.append(('KHACH_HANG', '=', self.khach_hang.id))

        if self.hang_hoa:
            domain.append(('HANG_HOA', '=', self.hang_hoa.id))

        if self.kho:
            domain.append(('KHO', '=', self.kho.id))
        #
        # if self.tscd:
        #     domain.append(('BO_PHAN', '=', self.bo_phan.id))
        #
        if self.bo_phan:
            domain.append(('BO_PHAN', '=', self.bo_phan.id))

        if self.khoan_muc:
            domain.append(('KHOAN_MUC', '=', self.khoan_muc.id))

        if self.vu_viec:
            domain.append(('VVIEC', '=', self.vu_viec.id))

        if self.thanh_pham:
            domain.append(('SAN_PHAM', '=', self.thanh_pham.id))

        user = self.env.user
        check = self.env['save.data'].sudo().search([('user_id', '=', user.id),
                                                     ('type', '=', "tk")])
        data = {
            "bao_cao": 1,
            "chung_tu": self.chung_tu or None,
            "so_hd": self.so_hd or None,
            "start_date": str(self.start_date) or "",
            "end_date": str(self.end_date) or "",
            "tai_khoan": self.tai_khoan.id or None,
            "chi_nhanh": self.chi_nhanh.id or None,
            "khach_hang": self.khach_hang.id or None,
            "hang_hoa": self.hang_hoa.id or None,
            "kho": self.kho.id or None,
            "tscd": self.tscd.id or None,
            "bo_phan": self.bo_phan.id or None,
            "khoan_muc": self.khoan_muc.id or None,
            "vu_viec": self.vu_viec.id or None,
            "thanh_pham": self.thanh_pham.id or None,
            "user_id": user.id,
            "type": "tk",
        }
        if check:
            check.update(data)
        else:
            self.env['save.data'].sudo().create(data)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tổng hợp',
            'res_model': 'nl.acc.tong.hop',
            'view_mode': 'tree,form',
            'domain': domain,
            'target': 'current',
        }
