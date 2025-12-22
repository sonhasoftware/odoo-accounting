from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccKchuyen(models.Model):
    _name = 'acc.kchuyen'

    TU_TK = fields.Char(string="Từ TK", store=True)
    SANG_TK = fields.Char(string="Sang TK", store=True)
    LAN = fields.Integer(string="Lần thứ", store=True)
    TU_BEN = fields.Integer(string="Từ bên(1 Nợ, 2 Có)", store=True)