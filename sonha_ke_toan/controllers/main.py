from odoo import http
from odoo.http import request


class FieldConfirmController(http.Controller):

    @http.route('/field_confirm/get_fields', type='json', auth='user')
    def get_fields(self, model):

        # trả về danh sách tên field cần confirm (['ma','cap',...])
        return request.env['field.confirm.config'].sudo().get_confirm_fields_for_model(model)

