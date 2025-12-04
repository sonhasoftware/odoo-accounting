from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccThue(models.Model):
    _name = 'acc.thue'
    _rec_name = 'TEN'

    TEN = fields.Char("Tên thuế", required=True)
    PT_THUE = fields.Integer("% Thuế", required=True)
