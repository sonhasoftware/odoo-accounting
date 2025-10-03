from odoo import models, fields, api


class FieldConfirmConfig(models.Model):
    _name = "field.confirm.config"
    _description = "Cấu hình xác nhận sửa field"

    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade"
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        required=True,
        domain="[('model_id', '=', model_id)]",
        ondelete="cascade"
    )
    require_confirm = fields.Boolean(string="Bắt xác nhận?", default=True)

    @api.model
    def get_confirm_fields_for_model(self, model_name):
        """Trả về list tên field (strings) cần confirm cho model_name"""
        configs = self.search([
            ('model_id.model', '=', model_name),
            ('require_confirm', '=', True)
        ])
        return configs.mapped('field_id.name')