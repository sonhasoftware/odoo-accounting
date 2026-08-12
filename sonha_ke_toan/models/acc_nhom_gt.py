from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccNhomGT(models.Model):
    _name = 'acc.nhom.gt'

    oke = fields.Float("OK")
    ma = fields.Char("Mã")
    ten = fields.Char("Tên")
    dk = fields.Char("DK")
    fun_truoc = fields.Char("Fun Trước")
    fun_sau = fields.Char("Fun Sau")
    tinh_gv = fields.Char("Tính GV")

    kc_bo_phan = fields.Boolean(string='Bộ phận', default=False)

    kc_vu_viec = fields.Boolean(string='Vụ việc', default=False)

    kc_khach_hang = fields.Boolean(string='Khách hàng', default=False)

    kc_tscd = fields.Boolean(string='TSCĐ', default=False)

    kc_khoan_muc = fields.Boolean(string='Khoản mục', default=False)

    kc_phan_xuong = fields.Boolean(string='Phân xưởng', default=False)

    kc_dtcp_tp = fields.Boolean(string='DTCP TP', default=False)

    kc_vlsphh = fields.Boolean(string='VLSPHH', default=False)

    kc_kho = fields.Boolean(string='Kho', default=False)

    pb_bo_phan = fields.Boolean(string='Bộ phận', default=False)

    pb_vu_viec = fields.Boolean(string='Vụ việc', default=False)

    pb_khach_hang = fields.Boolean(string='Khách hàng', default=False)

    pb_tscd = fields.Boolean(string='TSCĐ', default=False)

    pb_khoan_muc = fields.Boolean(string='Khoản mục', default=False)

    pb_phan_xuong = fields.Boolean(string='Phân xưởng', default=False)

    pb_dtcp_tp = fields.Boolean(string='DTCP TP', default=False)

    pb_vlsphh = fields.Boolean(string='VLSPHH', default=False)

    pb_kho = fields.Boolean(string='Kho', default=False)

    tieu_thuc_so_luong = fields.Boolean(
        string='Số lượng',
        default=False
    )

    tieu_thuc_tien = fields.Boolean(
        string='Tiền',
        default=False
    )