# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SonhaListColumnWidth(models.Model):
    _name = 'sonha.list.column.width'
    _description = 'List view column width preference'
    _rec_name = 'field_name'
    _order = 'model_name, view_key, field_name'

    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user, ondelete='cascade')
    model_name = fields.Char(required=True, index=True)
    view_key = fields.Char(required=True, default='default', index=True)
    field_name = fields.Char(required=True, index=True)
    width = fields.Integer(required=True)

    _sql_constraints = [
        (
            'sonha_column_width_unique',
            'unique(user_id, model_name, view_key, field_name)',
            'Column width is already configured for this user, model, view and field.',
        ),
    ]

    @api.model
    def get_widths(self, model_name, view_key='default'):
        if not model_name:
            return {}
        rows = self.sudo().search([
            ('user_id', '=', self.env.uid),
            ('model_name', '=', model_name),
            ('view_key', '=', view_key or 'default'),
        ])
        return {row.field_name: row.width for row in rows if row.field_name and row.width}

    @api.model
    def save_widths(self, model_name, view_key='default', widths=None):
        if not model_name or not isinstance(widths, dict):
            return False
        view_key = view_key or 'default'
        for field_name, width in widths.items():
            try:
                width = int(width)
            except (TypeError, ValueError):
                continue
            if not field_name or width <= 0:
                continue
            vals = {
                'user_id': self.env.uid,
                'model_name': model_name,
                'view_key': view_key,
                'field_name': field_name,
                'width': width,
            }
            record = self.sudo().search([
                ('user_id', '=', self.env.uid),
                ('model_name', '=', model_name),
                ('view_key', '=', view_key),
                ('field_name', '=', field_name),
            ], limit=1)
            if record:
                record.write({'width': width})
            else:
                self.sudo().create(vals)
        return True
