from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class DanhMucPhieuIn(models.Model):
    _name = 'danh.muc.phieu.in'

    ten = fields.Char('Tên phiếu in')
    temp = fields.Binary("Template", required=True)
    temp_filename = fields.Char("Tên file template")
    menu = fields.Many2one('ir.ui.menu')
    model_id = fields.Many2one('ir.model', string="Model chứng từ", help="Chỉ hiển thị phiếu in này cho model chứng từ tương ứng. Để trống nếu dùng chung.")
