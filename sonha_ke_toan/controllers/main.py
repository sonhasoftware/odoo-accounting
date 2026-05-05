from odoo import http
from odoo.http import request
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class FieldConfirmController(http.Controller):

    @http.route('/field_confirm/get_fields', type='json', auth='user')
    def get_fields(self, model):

        # trả về danh sách tên field cần confirm (['ma','cap',...])
        return request.env['field.confirm.config'].sudo().get_confirm_fields_for_model(model)

    @http.route("/sonha/get_allowed_models", type="json", auth="user")
    def get_allowed_models(self):
        user = request.env.user
        models = request.env["sonha.phan.quyen"].sudo().search([
            ("NGUOI_DUNG", "=", user.id),
            ("XEM_DM", "=", True),
        ]).mapped("TEN_BANG")
        return models

    @http.route('/field_confirm/get_confirm_fields', type='json', auth='user')
    def get_confirm_fields(self, model):
        fields = request.env['sonha.xac.nhan'].sudo().search([('MODEL_ID.model', '=', model),
                                                              ('REQUIRE_CONFIRM', '=', True)])
        field_names = fields.mapped('FIELD_ID.name')
        return field_names

    @http.route('/download/phieu_nhap/<int:record_id>', type='http', auth='user')
    def download_pdf(self, record_id, **kwargs):
        record = request.env['nl.acc.ap.h'].browse(record_id)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        p.drawString(100, 750, "Hello Odoo PDF")
        p.drawString(100, 730, f"Record ID: {record.id}")

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        return request.make_response(
            pdf,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="phieu_nhap_{record.id}.pdf"')
            ]
        )