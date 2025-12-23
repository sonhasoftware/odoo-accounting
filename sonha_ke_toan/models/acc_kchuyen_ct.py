from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccKchuyenCt(models.Model):
    _name = 'acc.kchuyen.ct'

    TU_TK_ID = fields.Many2one('acc.tai.khoan', string="Từ TK", store=True)
    TU_TK_MA = fields.Char(related='TU_TK_ID.MA', string="Từ TK", store=True)
    SANG_TK_ID = fields.Many2one('acc.tai.khoan', string="Sang TK", store=True)
    SANG_TK_MA = fields.Char(related='SANG_TK_ID.MA', string="Sang TK", store=True)
    LAN = fields.Integer(string="Lần thứ", store=True)
    TU_BEN = fields.Integer(string="Từ bên(1 Nợ, 2 Có)", store=True)
    TIEN = fields.Integer(string="Tiền", store=True)