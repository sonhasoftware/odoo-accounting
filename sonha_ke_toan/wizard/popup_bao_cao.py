from odoo import models, fields, api
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta


class PopupBaoCao(models.TransientModel):
    _name = "popup.bao.cao"
    _description = "Báo cáo"

    bao_cao = fields.Many2one('acc.bao.cao', "Báo cáo", required=True)

    start_date = fields.Date("Từ ngày", required=True, default=lambda self: self.default_from_date())
    end_date = fields.Date("Đến ngày", required=True, default=lambda self: self.default_to_date())

    tai_khoan = fields.Many2one('acc.tai.khoan', string="Tài khoản")
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
        res = super(PopupBaoCao, self).default_get(fields_list)
        permission = self.env['save.data'].sudo().search([('user_id', '=', user.id),
                                                          ('type', '=', "bc")])

        res.update({
            "bao_cao": permission.bao_cao.id or None,
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
        now = fields.Datetime.now()
        time_from = now - timedelta(seconds=5)
        time_to = now + timedelta(seconds=5)
        dvcs = self.env.company.id
        bao_cao = self.bao_cao.id

        start_date = str(self.start_date)
        end_date = str(self.end_date)

        tai_khoan = self.tai_khoan.id or None
        chi_nhanh = self.chi_nhanh.id or None
        khach_hang = self.khach_hang.id or None
        hang_hoa = self.hang_hoa.id or None
        kho = self.kho.id or None
        tscd = self.tscd.id or None
        bo_phan = self.bo_phan.id or None
        khoan_muc = self.khoan_muc.id or None
        vu_viec = self.vu_viec.id or None
        thanh_pham = self.thanh_pham.id or None
        id_rec = None

        vals = [dvcs, bao_cao, start_date, end_date, tai_khoan, chi_nhanh, khach_hang,
                hang_hoa, kho, tscd, bo_phan, khoan_muc, vu_viec, thanh_pham, now, id_rec]
        sql = self.bao_cao.FN_BAO_CAO
        self.env.cr.execute(sql, vals)
        domain = [('id_bc', '=', self.bao_cao.id),
                  ('create_date', '>=', time_from),
                  ('create_date', '<=', time_to),]

        user = self.env.user
        check = self.env['save.data'].sudo().search([('user_id', '=', user.id),
                                                     ('type', '=', "bc")])
        data = {
            "bao_cao": self.bao_cao.id or None,
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
            "type": "bc",
        }

        if check:
            check.update(data)
        else:
            self.env['save.data'].sudo().create(data)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Báo cáo',
            'res_model': 'nl.acc.bao.cao',
            'view_mode': 'tree',
            'domain': domain,
            'target': 'current',
            'context': {
                'search_default_bao_cao_id': self.id,
            }
        }

    def action_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Danh mục báo cáo',
            'res_model': 'acc.bao.cao',
            'view_mode': 'tree',
            'target': 'current',

        }