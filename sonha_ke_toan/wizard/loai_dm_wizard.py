from odoo import models, fields, api


class LoaiDMWizard(models.TransientModel):
    _name = "loai.dm.wizard"
    _description = "Wizard xác nhận mở menu"

    LOAI_DM = fields.Selection([('bo', "Bộ"),
                                ('sp', "SP"),
                                ('khac', "Khác")],
                               string="Loại DM", store=True)
    record_id = fields.Integer("ID sản phẩm")

    def action_confirm_open(self):
        self.ensure_one()
        record = self.record_id
        sp = self.env['acc.san.pham'].sudo().search([('id', '=', record)])
        dl = self.env['acc.bom'].sudo().search([('SAN_PHAM', '=', sp.id),
                                                ('LOAI_DM', '=', self.LOAI_DM)])
        if dl:
            return {
                'name': 'Chọn loại DM',
                'type': 'ir.actions.act_window',
                'res_model': 'acc.bom',
                'view_mode': 'tree',
                'target': 'current',
                'domain': [('id', '=', dl.ids)],
            }
        else:
            dl = self.env['acc.bom'].sudo().create({
                'SAN_PHAM': sp.id,
                'LOAI_DM': self.LOAI_DM
            })
            return {
                'name': 'Chọn loại DM',
                'type': 'ir.actions.act_window',
                'res_model': 'acc.bom',
                'view_mode': 'tree',
                'target': 'current',
                'domain': [('id', '=', dl.ids)],
            }
