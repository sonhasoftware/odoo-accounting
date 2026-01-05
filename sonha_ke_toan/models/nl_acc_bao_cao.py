from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


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

    @api.model
    def action_exit(self, ids):
        if not ids:
            raise ValidationError("Bạn chưa chọn bản ghi nào")
        records = self.browse(ids)
        if len(records) > 1:
            raise ValidationError("Bạn chỉ được phép chọn 1 bản ghi duy nhất!")

        dvcs = self.env.company.id
        bao_cao = records.id_bc

        start_date = None
        end_date = None

        tai_khoan = None
        chi_nhanh = None
        khach_hang = None
        hang_hoa = None
        kho = None
        tscd = None
        bo_phan = None
        khoan_muc = None
        vu_viec = None
        thanh_pham = None
        id_rec = records.id
        now = fields.Datetime.now()
        vals = [dvcs, bao_cao, start_date, end_date, tai_khoan, chi_nhanh, khach_hang,
                hang_hoa, kho, tscd, bo_phan, khoan_muc, vu_viec, thanh_pham, now, id_rec]

        time_from = now - timedelta(seconds=3)
        time_to = now + timedelta(seconds=3)

        fn_bao_cao = self.env['acc.bao.cao'].browse(bao_cao)

        sql = fn_bao_cao.FN_GOI_BC
        self.env.cr.execute(sql, vals)
        domain = [('id_bc', '=', bao_cao),
                  ('create_date', '>=', time_from),
                  ('create_date', '<=', time_to)]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Báo cáo',
            'res_model': 'nl.acc.bao.cao',
            'views': [(False, 'tree')],
            'domain': domain,
            'target': 'current',
        }
