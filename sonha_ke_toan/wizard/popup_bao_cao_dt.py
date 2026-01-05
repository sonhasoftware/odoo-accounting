from odoo import models, fields, api
from datetime import timedelta


class PopupBaoCaoDT(models.TransientModel):
    _name = "popup.bao.cao.dt"
    _description = "Báo cáo"

    bao_cao = fields.Many2one('acc.bao.cao', "Báo cáo", required=True)

    start_date = fields.Date("Từ ngày", required=True)
    end_date = fields.Date("Đến ngày", required=True)

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

        vals = [dvcs, bao_cao, start_date, end_date, tai_khoan, chi_nhanh, khach_hang,
                hang_hoa, kho, tscd, bo_phan, khoan_muc, vu_viec, thanh_pham, now]
        sql = self.bao_cao.FN_BAO_CAO
        self.env.cr.execute(sql, vals)
        domain = [('id_bc', '=', self.bao_cao.id),
                  ('create_date', '>=', time_from),
                  ('create_date', '<=', time_to),]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Báo cáo',
            'res_model': 'nl.acc.bao.cao',
            'view_mode': 'tree',
            'domain': domain,
            'target': 'current',
        }

    def action_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Danh mục báo cáo',
            'res_model': 'acc.bao.cao',
            'view_mode': 'tree',
            'target': 'current',

        }