from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class NLAccTongHop(models.Model):
    _name = 'nl.acc.tong.hop'

    ACC_AP_D = fields.Many2one('nl.acc.ap.d', string="ACC AP D", store=True)
    ACC_NK_D = fields.Many2one('acc.ap.nk.d', string="ACC AP NK D", store=True)

