# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TreeViewColumnPreference(models.Model):
    _name = "tree.view.column.preference"
    _description = "Tree View Column Preference"
    _rec_name = "key"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        ondelete="cascade",
        index=True,
    )
    key = fields.Char(required=True, index=True)
    value = fields.Text(required=True, default="{}")

    _sql_constraints = [
        ("user_key_unique", "unique(user_id, key)", "A column preference already exists for this user and key."),
    ]

    @api.model
    def get_values(self, keys):
        if not keys:
            return {}
        records = self.search([("user_id", "=", self.env.uid), ("key", "in", keys)])
        return {record.key: record.value for record in records}

    @api.model
    def set_value(self, key, value):
        record = self.search([("user_id", "=", self.env.uid), ("key", "=", key)], limit=1)
        vals = {"user_id": self.env.uid, "key": key, "value": value or "{}"}
        if record:
            record.write({"value": vals["value"]})
        else:
            record = self.create(vals)
        return record.id
