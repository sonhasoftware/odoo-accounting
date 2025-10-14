from odoo import models, fields, api


class SonhaXacNhan(models.Model):
    _name = "sonha.xac.nhan"
    _description = "Cấu hình xác nhận sửa field"

    MODEL_ID = fields.Many2one(
        "ir.model",
        string="Bảng",
        required=True,
        ondelete="cascade"
    )
    FIELD_ID = fields.Many2one(
        "ir.model.fields",
        string="Trường",
        required=True,
        domain="[('model_id', '=', MODEL_ID)]",
        ondelete="cascade"
    )
    REQUIRE_CONFIRM = fields.Boolean(string="Xác nhận(hỏi trước khi sửa)", default=False)
    CAM_SUA_FIELD = fields.Boolean(string="Cấm sửa", default=False)
    BAT_BUOC_FIELD = fields.Boolean(string="Trường bắt buộc", default=False)

    @api.model
    def get_confirm_fields_for_model(self, model_name):
        """Trả về list tên field (strings) cần confirm cho model_name"""
        configs = self.search([
            ('MODEL_ID.model', '=', model_name),
            ('REQUIRE_CONFIRM', '=', True)
        ])
        return configs.mapped('field_id.name')