from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class DanhMucPhieuIn(models.Model):
    _name = 'danh.muc.phieu.in'

    ten = fields.Char('Tên phiếu in')
    temp = fields.Binary("Template")
    menu = fields.Many2one('ir.ui.menu')
