# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models


class SonhaAccountingLog(models.Model):
    _name = 'sonha.accounting.log'
    _description = 'Nhật ký tạo sửa xóa dữ liệu kế toán'
    _order = 'action_datetime desc, id desc'
    _rec_name = 'record_display_name'

    user_id = fields.Many2one(
        'res.users',
        string='Người dùng',
        required=True,
        index=True,
        ondelete='restrict',
        default=lambda self: self.env.user,
    )
    action = fields.Selection(
        [
            ('create', 'Tạo'),
            ('write', 'Sửa'),
            ('unlink', 'Xóa'),
        ],
        string='Hành động',
        required=True,
        index=True,
    )
    action_datetime = fields.Datetime(
        string='Ngày giờ thao tác',
        required=True,
        index=True,
        default=fields.Datetime.now,
    )
    model_name = fields.Char(string='Model', required=True, index=True)
    table_name = fields.Char(string='Bảng', required=True, index=True)
    record_id = fields.Integer(string='ID bản ghi', required=True, index=True)
    record_display_name = fields.Char(string='Bản ghi')
    old_values = fields.Text(string='Dữ liệu cũ')
    new_values = fields.Text(string='Dữ liệu mới')


class SonhaAccountingAuditBase(models.AbstractModel):
    _inherit = 'base'

    _sonha_accounting_audit_module = 'sonha_ke_toan'
    _sonha_accounting_audit_excluded_models = {
        'sonha.accounting.log',
        'nl.acc.tong.hop.log',
        'save.data',
    }

    def _sonha_audit_model_belongs_to_module(self):
        module_name = getattr(type(self), '_module', None) or getattr(self, '_module', None)
        if module_name == self._sonha_accounting_audit_module:
            return True

        model_xmlid = 'model_%s' % self._name.replace('.', '_')
        return bool(self.env['ir.model.data'].sudo().search_count([
            ('module', '=', self._sonha_accounting_audit_module),
            ('model', '=', 'ir.model'),
            ('name', '=', model_xmlid),
        ]))

    def _sonha_audit_enabled(self):
        if self.env.context.get('sonha_skip_accounting_log'):
            return False
        if self._name in self._sonha_accounting_audit_excluded_models:
            return False
        if not getattr(self, '_auto', False):
            return False
        is_transient = getattr(self, 'is_transient', None)
        if is_transient and is_transient():
            return False
        return self._sonha_audit_model_belongs_to_module()

    def _sonha_audit_value(self, record, field_name):
        field = record._fields.get(field_name)
        if not field:
            return False

        value = record[field_name]
        if field.type == 'many2one':
            return value.id if value else False
        if field.type in ('one2many', 'many2many'):
            return value.ids
        if field.type == 'date':
            return fields.Date.to_string(value) if value else False
        if field.type == 'datetime':
            return fields.Datetime.to_string(value) if value else False
        return value

    def _sonha_audit_json(self, data):
        return json.dumps(data, ensure_ascii=False, default=str)

    def _sonha_audit_record_name(self, record):
        display_name = getattr(record, 'display_name', False)
        return display_name or '%s,%s' % (record._name, record.id)

    def _sonha_audit_old_values(self, vals):
        field_names = [field_name for field_name in vals if field_name in self._fields]
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field_name: self._sonha_audit_value(record, field_name)
                for field_name in field_names
            }
        return old_values

    def _sonha_audit_log(self, action, records, vals_by_id=None, old_values_by_id=None, names_by_id=None):
        if not records or not records._sonha_audit_enabled():
            return

        action_datetime = fields.Datetime.now()
        log_values = []
        for record in records:
            log_values.append({
                'user_id': self.env.uid,
                'action': action,
                'action_datetime': action_datetime,
                'model_name': record._name,
                'table_name': record._table,
                'record_id': record.id,
                'record_display_name': (
                    names_by_id or {}
                ).get(record.id) or self._sonha_audit_record_name(record),
                'old_values': self._sonha_audit_json((old_values_by_id or {}).get(record.id, {})),
                'new_values': self._sonha_audit_json((vals_by_id or {}).get(record.id, {})),
            })

        if log_values:
            self.env['sonha.accounting.log'].sudo().with_context(
                sonha_skip_accounting_log=True,
            ).create(log_values)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if records._sonha_audit_enabled():
            vals_by_id = {}
            for record, vals in zip(records, vals_list):
                vals_by_id[record.id] = vals
            records._sonha_audit_log('create', records, vals_by_id=vals_by_id)
        return records

    def write(self, vals):
        audit_enabled = self._sonha_audit_enabled()
        old_values_by_id = self._sonha_audit_old_values(vals) if audit_enabled else {}
        names_by_id = {
            record.id: self._sonha_audit_record_name(record)
            for record in self
        } if audit_enabled else {}

        result = super().write(vals)

        if audit_enabled:
            vals_by_id = {record.id: vals for record in self}
            self._sonha_audit_log(
                'write',
                self,
                vals_by_id=vals_by_id,
                old_values_by_id=old_values_by_id,
                names_by_id=names_by_id,
            )
        return result

    def unlink(self):
        audit_enabled = self._sonha_audit_enabled()
        old_values_by_id = {}
        names_by_id = {}
        if audit_enabled:
            field_names = [field_name for field_name in self._fields if field_name != 'id']
            for record in self:
                old_values_by_id[record.id] = {
                    field_name: self._sonha_audit_value(record, field_name)
                    for field_name in field_names
                }
                names_by_id[record.id] = self._sonha_audit_record_name(record)

        records = self
        result = super().unlink()

        if audit_enabled:
            records._sonha_audit_log(
                'unlink',
                records,
                old_values_by_id=old_values_by_id,
                names_by_id=names_by_id,
            )
        return result
