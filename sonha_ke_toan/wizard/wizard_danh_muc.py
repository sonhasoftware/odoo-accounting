from urllib.parse import quote

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardDanhMuc(models.TransientModel):
    _name = 'wizard.danh.muc'

    phieu_in = fields.Many2one('danh.muc.phieu.in', string="Phiếu in", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        if active_model:
            model = self.env['ir.model'].sudo().search([('model', '=', active_model)], limit=1)
            if model:
                candidates = self.env['danh.muc.phieu.in'].sudo().search([
                    '|', ('model_id', '=', model.id), ('model_id', '=', False),
                ], limit=1)
                if candidates:
                    res['phieu_in'] = candidates.id
        return res

    def action_print(self):
        self.ensure_one()
        if not self.phieu_in:
            raise UserError(_('Vui lòng chọn phiếu in.'))
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if not active_model or not active_id:
            raise UserError(_('Không xác định được chứng từ cần in.'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/download/dynamic_phieu_in/%s?model=%s&record_id=%s' % (
                self.phieu_in.id,
                quote(active_model),
                active_id,
            ),
            'target': 'self',
        }
