from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


BUS_NOTIFICATION_TYPE = "tree_view_column_layout/updated"


class TreeViewColumnLayout(models.Model):
    _name = "tree.view.column.layout"
    _description = "Shared Tree View Column Layout"
    _order = "view_id"

    view_id = fields.Many2one(
        "ir.ui.view",
        required=True,
        index=True,
        ondelete="cascade",
    )
    res_model = fields.Char(related="view_id.model", store=True, readonly=True, index=True)
    column_order = fields.Json(default=lambda self: [])
    column_widths = fields.Json(default=lambda self: {})
    column_labels = fields.Json(default=lambda self: {})
    revision = fields.Integer(default=1, readonly=True)

    _sql_constraints = [
        ("view_id_unique", "unique(view_id)", "A column layout already exists for this view."),
    ]

    @api.model
    def _sanitize_column_order(self, column_order):
        if not isinstance(column_order, list):
            raise ValidationError(_("Column order must be a list."))
        result = []
        for name in column_order:
            if isinstance(name, str) and name and name not in result:
                result.append(name[:128])
        return result[:500]

    @api.model
    def _sanitize_width_updates(self, width_updates):
        if not isinstance(width_updates, dict):
            raise ValidationError(_("Column width updates must be an object."))
        result = {}
        for name, width in width_updates.items():
            if not isinstance(name, str) or not name:
                continue
            if width is None or width is False:
                result[name[:128]] = None
                continue
            if isinstance(width, bool) or not isinstance(width, (int, float)):
                continue
            result[name[:128]] = max(24, min(2000, round(width)))
        return result

    @api.model
    def _sanitize_label_updates(self, label_updates):
        if not isinstance(label_updates, dict):
            raise ValidationError(_("Column label updates must be an object."))
        result = {}
        for key, label in label_updates.items():
            if not isinstance(key, str) or not key:
                continue
            key = key[:160]
            if label is None or label is False:
                result[key] = None
                continue
            if not isinstance(label, str):
                continue
            label = label.strip()
            result[key] = label[:128] if label else None
        return result

    def _format_layout(self):
        self.ensure_one()
        return {
            "viewId": self.view_id.id,
            "resModel": self.res_model,
            "order": self.column_order if isinstance(self.column_order, list) else [],
            "widths": self.column_widths if isinstance(self.column_widths, dict) else {},
            "labels": self.column_labels if isinstance(self.column_labels, dict) else {},
            "revision": self.revision,
        }

    @api.model
    def _get_layout_map(self):
        return {
            str(layout.view_id.id): layout._format_layout()
            for layout in self.sudo().search([])
        }

    @api.model
    def save_layout(
        self,
        view_id,
        column_order=None,
        width_updates=None,
        label_updates=None,
        reset=False,
    ):
        if not self.env.user._is_admin():
            raise AccessError(_("Only administrators can change shared column layouts."))

        try:
            view_id = int(view_id)
        except (TypeError, ValueError):
            raise ValidationError(_("Invalid view identifier."))

        view = self.env["ir.ui.view"].sudo().browse(view_id).exists()
        if not view or view.type != "tree":
            raise ValidationError(_("The selected view is not a list view."))

        layout = self.sudo().search([("view_id", "=", view.id)], limit=1)
        values = {
            "view_id": view.id,
            "revision": (layout.revision if layout else 0) + 1,
        }

        if reset:
            values.update({"column_order": [], "column_widths": {}, "column_labels": {}})
        else:
            if column_order is not None:
                values["column_order"] = self._sanitize_column_order(column_order)
            if width_updates is not None:
                widths = dict(layout.column_widths or {}) if layout else {}
                for name, width in self._sanitize_width_updates(width_updates).items():
                    if width is None:
                        widths.pop(name, None)
                    else:
                        widths[name] = width
                values["column_widths"] = widths
            if label_updates is not None:
                labels = dict(layout.column_labels or {}) if layout else {}
                for key, label in self._sanitize_label_updates(label_updates).items():
                    if label is None:
                        labels.pop(key, None)
                    else:
                        labels[key] = label
                values["column_labels"] = labels

        if layout:
            layout.write(values)
        else:
            layout = self.sudo().create(values)

        payload = layout._format_layout()
        self.env["bus.bus"].sudo()._sendone("broadcast", BUS_NOTIFICATION_TYPE, payload)
        return payload
