from odoo import api, fields, models


class SonhaPhanQuyen(models.Model):
    _name = 'sonha.phan.quyen'

    NGUOI_DUNG = fields.Many2one('sonha.user', string="Người dùng")
    TEN_BANG = fields.Many2one('ir.model', string="Tên Bảng")
    XEM_DM = fields.Boolean(string="Xem DM", default=False)
    THEM_DM = fields.Boolean(string="Thêm DM", default=False)
    SUA_DM = fields.Boolean(string="Sửa DM", default=False)
    XOA_DM = fields.Boolean(string="Xóa DM", default=False)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True)

    THEM_DL = fields.Boolean(string="Thêm mới DL", default=False)
    XEM_DL = fields.Many2many('sonha.user', 'xem_dl_rel', 'xem_dl_phan_quyen', 'xem_dl_id',
                                 string="Xem DL của User")
    SUA_DL = fields.Many2many('sonha.user', 'sua_dl_rel', 'sua_dl_phan_quyen', 'sua_dl_id',
                              string="Sửa DL của User")

    _sql_constraints = [
        ('unique_user_model', 'unique(NGUOI_DUNG, TEN_BANG)',
         'Mỗi user chỉ có 1 phân quyền cho 1 model!'),
    ]
