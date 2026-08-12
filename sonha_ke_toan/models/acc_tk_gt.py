from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccTkGt(models.Model):
    _name = 'acc.tk.gt'

    tu_tk = fields.Char("Từ TK")
    sang_tk = fields.Char("Sang TK")
    ghi_chu = fields.Char("Ghi chú")
    nhom_gt = fields.Many2one('acc.nhom.gt')