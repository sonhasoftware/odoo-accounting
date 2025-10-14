from odoo import api, fields, models


class SonhaBTThem(models.Model):
    _name = 'sonha.bt.them'

    MENU = fields.Many2one('ir.ui.menu', string="ID MENU", store=True)

    MA_TK0_ID = fields.Many2one('acc.tai.khoan', string="Nợ", store=True)
    MA_TK0 = fields.Char(related='MA_TK0_ID.MA', string="Nợ", store=True)

    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True)
    MA_TK1 = fields.Char(related='MA_TK1_ID.MA', string="Có", store=True)

    DK = fields.Char(string="DK", store=True)
    CO_SL = fields.Boolean(string="Có SL", store=True)
