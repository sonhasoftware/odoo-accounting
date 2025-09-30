from odoo import api, fields, models


class SonhaPhanQuyen(models.Model):
    _name = 'sonha.phan.quyen'

    NGUOI_DUNG = fields.Many2one('sonha.user', string="Người dùng", store=True)
    TEN_BANG = fields.Many2one('ir.model', string="Mã Bảng", store=True)
    # đây là mã bảng model
    MA_BANG = fields.Char(related='TEN_BANG.model', string="Tên Bảng", store=True)
    # đây là tên bảng
    XEM_DM = fields.Boolean(string="Xem DM", default=False, store=True)
    THEM_DM = fields.Boolean(string="Thêm DM", default=False, store=True)
    SUA_DM = fields.Boolean(string="Sửa DM", default=False, store=True)
    XOA_DM = fields.Boolean(string="Xóa DM", default=False, store=True)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True)

    THEM_DL = fields.Boolean(string="Thêm mới DL", default=False, store=True)
    XEM_DL = fields.Many2many('sonha.user', 'xem_dl_rel', 'xem_dl_phan_quyen', 'xem_dl_id',
                                 string="Xem DL của User", store=True)
    SUA_DL = fields.Many2many('sonha.user', 'sua_dl_rel', 'sua_dl_phan_quyen', 'sua_dl_id',
                              string="Sửa DL của User", store=True)

    _sql_constraints = [
        ('unique_user_model', 'unique(NGUOI_DUNG, TEN_BANG)',
         'Mỗi user chỉ có 1 phân quyền cho 1 model!'),
    ]
