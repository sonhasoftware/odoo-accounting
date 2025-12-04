from odoo import models, fields, api


class AccThongBao(models.TransientModel):
    _name = 'thong.bao.wizard'

    TIEU_DE = fields.Text(string="Tiêu đề")
    NOI_DUNG = fields.Text(string="Nội dung")