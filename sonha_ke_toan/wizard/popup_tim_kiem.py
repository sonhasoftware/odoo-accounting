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

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tổng hợp',
            'res_model': 'nl.acc.tong.hop',
            'view_mode': 'tree,form',
            'domain': domain,
            'target': 'current',
        }
