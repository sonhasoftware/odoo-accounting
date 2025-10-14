from odoo import models, fields


class VAccSanPham(models.Model):
    _name = 'v.acc.san.pham'
    _description = 'View Sản Phẩm'
    _auto = False

    # Các field phải đúng với cột trong view SQL
    MA = fields.Char("Mã")
    TEN = fields.Char("TEN")
    SAN_PHAM = fields.Integer("Sản phẩm")

    def action_view_bom(self):
        return {
            'name': 'Chọn loại DM',
            'type': 'ir.actions.act_window',
            'res_model': 'loai.dm.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_record_id': self.SAN_PHAM,
            },
        }
