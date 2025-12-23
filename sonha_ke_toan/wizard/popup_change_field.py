from odoo import api, fields, models, _


class PopupChangeField(models.TransientModel):
    _name = "popup.change.field"

    record_id = fields.Integer()
    field_name = fields.Char()
    value = fields.Float(string="Giá trị")

    @api.model
    def open_from_list(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "target": "new",
        }

    def action_confirm(self):
        pass
    #     rec = self.env["your.model"].browse(self.record_id)
    #     rec.write({
    #         self.field_name: self.value
    #     })
