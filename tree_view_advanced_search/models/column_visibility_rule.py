from odoo import api, fields, models


class ColumnVisibilityRule(models.Model):
    _name = "column.visibility.rule"
    _description = "Column Visibility Rule"

    name = fields.Char(required=True)
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    field_id = fields.Many2one(
        "ir.model.fields",
        required=True,
        domain="[('model_id', '=', model_id), ('store', '=', True)]",
        ondelete="cascade",
    )
    group_ids = fields.Many2many("res.groups", string="Allowed Groups", required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "model_field_unique",
            "unique(model_id, field_id)",
            "A visibility rule already exists for this field.",
        )
    ]

    @api.model
    def get_hidden_fields(self, model_name):
        user_groups = self.env.user.groups_id
        rules = self.search([("active", "=", True), ("model_id.model", "=", model_name)])
        hidden_fields = []
        for rule in rules:
            if not (rule.group_ids & user_groups):
                hidden_fields.append(rule.field_id.name)
        return hidden_fields
