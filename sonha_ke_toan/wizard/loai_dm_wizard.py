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

        sp = self.env['acc.san.pham'].sudo().browse(record)

        dl = self.env['acc.bom'].sudo().search([
            ('SAN_PHAM', '=', sp.id),
            ('LOAI_DM', '=', self.LOAI_DM)
        ], limit=1)

        if not dl:
            dl = self.env['acc.bom'].sudo().create({
                'SAN_PHAM': sp.id,
                'LOAI_DM': self.LOAI_DM
            })

        return {
            'name': 'Chọn loại DM',
            'type': 'ir.actions.act_window',
            'res_model': 'acc.bom',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', dl.ids)],
            'context': {
                # 🔥 CỰC KỲ QUAN TRỌNG
                'active_model': 'acc.bom',
                'active_id': dl.id,

                # 👉 nếu muốn default thêm khi create
                'default_SAN_PHAM': sp.id,
                'default_LOAI_DM': self.LOAI_DM,
            }
        }
