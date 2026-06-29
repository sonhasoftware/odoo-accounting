from odoo import models, fields, api


class WizardDanhMuc(models.TransientModel):
    _name = 'wizard.danh.muc'

    phieu_in = fields.Many2one('danh.muc.phieu.in', string="Phiếu in")

    def action_print(self):
        pass
