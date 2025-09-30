from odoo import api, fields, models


class AccBoPhan(models.Model):
    _name = 'acc.bo.phan'

    CAP = fields.Boolean(string="Cấp", store=True)
    MA = fields.Char(string="Mã", store=True)
    TEN = fields.Char(string="Tên", store=True)
    KHO = fields.Integer(string="Kho", store=True)
    DVCS = fields.Integer(string="ĐV", store=True)
    ACTIVE = fields.Boolean(string="ACTIVE", store=True)