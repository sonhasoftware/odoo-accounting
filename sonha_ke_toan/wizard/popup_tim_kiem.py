from odoo import models, fields, api


class PopupTimKiem(models.TransientModel):
    _name = "popup.tim.kiem"
    _description = "Tm kiếm dữ liệu"

    start_date = fields.Date("Từ ngày")
    end_date = fields.Date("Đến ngày")

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

    def action_search(self):
        pass
