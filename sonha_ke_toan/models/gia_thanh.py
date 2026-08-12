from odoo import models, fields


class GiaThanh(models.Model):
    _name = 'gia.thanh'
    _description = 'Giá thành'

    nhom = fields.Char(string='Nhóm')

    tai_khoan = fields.Char(string='TK')

    tk_auto = fields.Boolean(string='Auto', default=False)

    thang = fields.Integer(string='Tháng')

    nam = fields.Integer(string='Năm')

    dg_theo_tien = fields.Boolean(string='ĐG theo tiền',default=False)

    kc_bo_phan = fields.Boolean(string='Bộ phận',default=False)

    kc_vu_viec = fields.Boolean(string='Vụ việc',default=False)

    kc_khach_hang = fields.Boolean(string='Khách hàng',default=False)

    kc_tscd = fields.Boolean(string='TSCĐ',default=False)

    kc_khoan_muc = fields.Boolean(string='Khoản mục',default=False)

    kc_phan_xuong = fields.Boolean(string='Phân xưởng',default=False)

    kc_dtcp_tp = fields.Boolean(string='DTCP TP', default=False)

    kc_vlsphh = fields.Boolean(string='VLSPHH',default=False)

    kc_kho = fields.Boolean(string='Kho',default=False)

    pb_bo_phan = fields.Boolean(string='Bộ phận',default=False)

    pb_vu_viec = fields.Boolean(string='Vụ việc',default=False)

    pb_khach_hang = fields.Boolean(string='Khách hàng',default=False)

    pb_tscd = fields.Boolean(string='TSCĐ',default=False)

    pb_khoan_muc = fields.Boolean(string='Khoản mục',default=False)

    pb_phan_xuong = fields.Boolean(string='Phân xưởng',default=False)

    pb_dtcp_tp = fields.Boolean(string='DTCP TP',default=False)

    pb_vlsphh = fields.Boolean(string='VLSPHH',default=False)

    pb_kho = fields.Boolean(string='Kho',default=False)


    tieu_thuc_so_luong = fields.Boolean(
        string='Số lượng',
        default=False
    )

    tieu_thuc_tien = fields.Boolean(
        string='Tiền',
        default=False
    )

    def action_handle(self):
        return {'type': 'ir.actions.act_window_close'}
