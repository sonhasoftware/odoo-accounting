# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models


class SonhaLog(models.Model):
    _name = 'sonha.log'
    _description = 'Sơn Hà Audit Log'
    _order = 'create_date desc, id desc'

    model_name = fields.Char(string='Model', required=True, index=True)
    res_id = fields.Integer(string='Record ID', required=True, index=True)
    action = fields.Selection([
        ('write', 'Write'),
        ('unlink', 'Unlink'),
    ], string='Action', required=True, index=True)
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    old_values = fields.Text(string='Old Values')
    new_values = fields.Text(string='New Values')


class SonhaLogMixin(models.AbstractModel):
    _name = 'sonha.log.mixin'
    _description = 'Audit log for accounting module'

    @api.model
    def _sonha_should_log(self):
        allowed_prefixes = ('acc.', 'nl.acc.', 'account.')
        return (
            not self._transient
            and self._name != 'sonha.log'
            and self._name.startswith(allowed_prefixes)
        )

    def _sonha_capture_before(self, field_names):
        return {
            record.id: record.read(field_names)[0] if field_names else {}
            for record in self
        }

    def _sonha_create_write_logs(self, before_map, field_names):
        for record in self:
            old_values = before_map.get(record.id, {})
            new_values = record.read(field_names)[0] if field_names else {}
            self.env['sonha.log'].sudo().create({
                'model_name': self._name,
                'res_id': record.id,
                'action': 'write',
                'user_id': self.env.user.id,
                'old_values': json.dumps(old_values, ensure_ascii=False, default=str),
                'new_values': json.dumps(new_values, ensure_ascii=False, default=str),
            })

    def write(self, vals):
        if self.env.context.get('_sonha_log_handled') or not self._sonha_should_log() or not vals:
            return super().write(vals)

        tracked_fields = [fname for fname in vals if fname in self._fields]
        before_map = self._sonha_capture_before(tracked_fields)
        result = super(SonhaLogMixin, self.with_context(_sonha_log_handled=True)).write(vals)
        self._sonha_create_write_logs(before_map, tracked_fields)
        return result

    def unlink(self):
        if self.env.context.get('_sonha_log_handled') or not self._sonha_should_log():
            return super().unlink()

        all_fields = list(self._fields.keys())
        snapshot = {
            record.id: record.read(all_fields)[0]
            for record in self
        }

        for record in self:
            self.env['sonha.log'].sudo().create({
                'model_name': self._name,
                'res_id': record.id,
                'action': 'unlink',
                'user_id': self.env.user.id,
                'old_values': json.dumps(snapshot.get(record.id, {}), ensure_ascii=False, default=str),
                'new_values': False,
            })

        return super(SonhaLogMixin, self.with_context(_sonha_log_handled=True)).unlink()


class SonhaLogHook(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _sonha_should_log(self):
        # Reuse when models explicitly inherit sonha.log.mixin
        mixin = self.env.get('sonha.log.mixin')
        if mixin:
            return mixin._sonha_should_log.__get__(self, type(self))()
        allowed_prefixes = ('acc.', 'nl.acc.', 'account.')
        return (
            not self._transient
            and self._name != 'sonha.log'
            and self._name.startswith(allowed_prefixes)
        )

    def write(self, vals):
        if self.env.context.get('_sonha_log_handled') or not self._sonha_should_log() or not vals:
            return super().write(vals)

        tracked_fields = [fname for fname in vals if fname in self._fields]
        before_map = {
            record.id: record.read(tracked_fields)[0] if tracked_fields else {}
            for record in self
        }

        result = super(SonhaLogHook, self.with_context(_sonha_log_handled=True)).write(vals)

        for record in self:
            old_values = before_map.get(record.id, {})
            new_values = record.read(tracked_fields)[0] if tracked_fields else {}
            self.env['sonha.log'].sudo().create({
                'model_name': self._name,
                'res_id': record.id,
                'action': 'write',
                'user_id': self.env.user.id,
                'old_values': json.dumps(old_values, ensure_ascii=False, default=str),
                'new_values': json.dumps(new_values, ensure_ascii=False, default=str),
            })

        return result

    def unlink(self):
        if self.env.context.get('_sonha_log_handled') or not self._sonha_should_log():
            return super(SonhaLogHook, self.with_context(_sonha_log_handled=True)).unlink()

        all_fields = list(self._fields.keys())
        snapshot = {
            record.id: record.read(all_fields)[0]
            for record in self
        }

        for record in self:
            self.env['sonha.log'].sudo().create({
                'model_name': self._name,
                'res_id': record.id,
                'action': 'unlink',
                'user_id': self.env.user.id,
                'old_values': json.dumps(snapshot.get(record.id, {}), ensure_ascii=False, default=str),
                'new_values': False,
            })

        return super(SonhaLogHook, self.with_context(_sonha_log_handled=True)).unlink()
