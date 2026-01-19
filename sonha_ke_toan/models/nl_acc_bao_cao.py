from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
from lxml import etree


class NlAccBaoCao(models.Model):
    _name = 'nl.acc.bao.cao'
    _table = 'nl_acc_bao_cao'
    _auto = False

    ma_tk0 = fields.Char(string="TK")
    ma_tk1 = fields.Char(string="TK DU")
    ten_tk = fields.Char(string="Tên tk")
    hang_hoa = fields.Many2one('acc.hang.hoa', "Hàng hóa")
    ma_hang = fields.Char(string="Mã hàng")
    ten_hang = fields.Char(string="Tên hàng")
    so_luong = fields.Float(string="Số lượng")
    don_gia = fields.Float(string="Đơn giá")
    ps_no1 = fields.Integer(string="Thành tiền")
    ps_co1 = fields.Integer(string="PS có")
    ps_no_nte = fields.Integer(string="PS nợ ntệ")
    ps_co_nte = fields.Integer(string="PS có ntệ")
    du_no_dau = fields.Integer(string="Dư nợ đầu")
    du_co_dau = fields.Integer(string="Dư có đầu")
    du_no_cuoi = fields.Integer(string="Dư nợ cuối")
    du_no_cuoi_nte = fields.Integer(string="Dư nợ cuối ntệ")
    du_co_cuoi = fields.Integer(string="Dư có cuối")
    du_co_cuoi_nte = fields.Integer(string="Dư có cuối ntệ")
    tien_nte = fields.Float(string="Tiền ntệ")
    vat = fields.Integer(string="VAT")
    ngay_ct = fields.Date(string="Ngày CT")
    chung_tu = fields.Char(string="Chứng từ")
    ghi_chu = fields.Char(string="Diễn giải")
    khach_hang = fields.Many2one('acc.khach.hang', "Khách hàng")
    ma_kh = fields.Char(string="Mã KH")
    ten_kh = fields.Char(string="Tên KH")
    kh_thue = fields.Char(string="KH thuế")
    ms_thue = fields.Char(string="MS thuế")
    dc_thue = fields.Char(string="DC thuế")
    bo_phan = fields.Many2one('acc.bo.phan', "Bộ phận")
    ma_bp = fields.Char(string="Mã bp")
    ten_bp = fields.Char(string="Tên bp")
    vviec = fields.Many2one('acc.vviec', "Vụ việc")
    ma_vviec = fields.Char(string="Mã vviệc")
    ten_vviec = fields.Char(string="Tên vviệc")

    kho = fields.Many2one('acc.kho', "Kho")
    ma_kho = fields.Char(string="Mã kho")
    ten_kho = fields.Char(string="Tên kho")

    khoan_muc = fields.Many2one('acc.khoan.muc', "Khoản mục")
    ma_km = fields.Char(string="Mã khoản mục")
    ten_km = fields.Char(string="Tên khoản mục")

    tien_te = fields.Many2one('acc.tien.te', "Tiền tệ")
    dvcs = fields.Many2one('res.company', "DVCS")
    ty_gia = fields.Float("Tỷ giá")

    chi_nhanh = fields.Many2one('acc.chi.nhanh', "Chi nhánh")
    ma_cn = fields.Char(string="Mã chi nhánh")
    ten_cn = fields.Char(string="Tên chi nhánh")

    so_luong2 = fields.Float("Số lượng 2")
    sl_tp = fields.Float("Số lượng TP")
    nhom_vat = fields.Char("Nhóm VAT")

    san_pham = fields.Many2one('acc.san.pham', "Sản phẩm")
    ma_sp = fields.Char(string="Mã sản phẩm")
    ten_sp = fields.Char(string="Tên sản phẩm")

    nvbh = fields.Many2one('acc.nvbh', "NVBH")
    ma_nvbh = fields.Char(string="Mã NVBH")
    ten_nvbh = fields.Char(string="Tên NVBH")

    tscd = fields.Many2one('acc.tscd', "TSCĐ")
    ma_tscd = fields.Char(string="Mã TSCĐ")
    ten_tscd = fields.Char(string="Tên TSCĐ")

    para_bc = fields.Text(string="Para BC")

    tu_ngay = fields.Date(string="Para BC")
    den_ngay = fields.Text(string="Para BC")

    ma_tk0_id = fields.Many2one('acc.tai.khoan', "ID tài khoản 0")

    id_bc = fields.Integer(string="idbc")
    create_date = fields.Datetime("...")

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type != 'tree':
            return res

        record = self.search([], limit=1, order='id desc')
        bao_cao_id = record.id_bc if record and record.id_bc else None
        if not bao_cao_id:
            return res

        config = self.env['acc.bao.cao'].browse(bao_cao_id)
        allow_fields = set(config.field_ids.mapped('name'))

        arch = res.get('arch')
        if not arch:
            return res

        doc = etree.XML(arch)

        for field in doc.xpath("//field"):
            if field.get('name') not in allow_fields:
                field.getparent().remove(field)

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

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
