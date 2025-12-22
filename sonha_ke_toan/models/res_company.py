from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    ngay_khoa = fields.Date(string="Ngày khóa", required=True)
