from odoo import models, fields


class SaveData(models.Model):
    _name = 'save.data'

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
    user_id = fields.Many2one('res.users')
    type = fields.Selection([('bc', "Báo cáo"),
                             ('tk', "Tìm kiếm")],
                            string="Type")
    chung_tu = fields.Char(string="Chứng từ")
    so_hd = fields.Char(string="Số HĐ")
