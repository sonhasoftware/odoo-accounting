from odoo import models, fields, api


class NlAccBaoCao(models.Model):
    _name = 'nl.acc.bao.cao'
    _table = 'nl_acc_bao_cao'
    _auto = False

    ma_tk0 = fields.Char(string="TK0")
    ma_tk1 = fields.Char(string="TK1")
    ten_tk = fields.Char(string="Tên tk")
    hang_hoa = fields.Many2one('acc.hang.hoa', "Hàng hóa")
    so_luong = fields.Float(string="Số lượng")
    don_gia = fields.Float(string="Đơn giá")
    ps_no1 = fields.Integer(string="Thành tiền")
    tien_nte = fields.Float(string="Tiền ngoại tệ")
    vat = fields.Integer(string="VAT")
    ngay_ct = fields.Date(string="Ngày CT")
    chung_tu = fields.Char(string="Chứng từ")
    # ctgs = fields.Char(string="CTGS")
    # so_hd = fields.Char(string="Số HĐ")
    # seri_hd = fields.Char(string="Mã HĐ")
    # ngay_hd = fields.Date(string="Ngày HĐ")
    # # mau_so = fields.Char(string="Mẫu số")
    # pt_thue = fields.Integer(string="PT Thuế")
    # ong_ba = fields.Char(string="Ông bà")
    # ghi_chu = fields.Char(string="Ghi chú")
    id_bc = fields.Integer(string="idbc")
    # KHACH_HANG = fields.Float(string="Thành tiền")
    # KH_THUE = fields.Float(string="Thành tiền")
    # MS_THUE = fields.Float(string="Thành tiền")
    # DC_THUE = fields.Float(string="Thành tiền")
    # BO_PHAN = fields.Float(string="Thành tiền")
    # VVIEC = fields.Float(string="Thành tiền")
    # KHO = fields.Float(string="Thành tiền")
    # KHOAN_MUC = fields.Float(string="Thành tiền")
    # TIEN_TE = fields.Float(string="Thành tiền")
    # TY_GIA = fields.Float(string="Thành tiền")
    create_date = fields.Datetime("...")

    def action_exit(self, domain):
        records = self.search(domain)
        records.sudo().unlink()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Báo cáo',
            'res_model': 'popup.bao.cao.form',
            'view_mode': 'form',
            'target': 'new',
        }
