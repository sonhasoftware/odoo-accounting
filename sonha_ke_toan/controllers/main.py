from odoo import http
from odoo.http import request
import io
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


current_dir = os.path.dirname(os.path.abspath(__file__))

font_path = os.path.join(current_dir, '..', 'static', 'fonts', 'DejaVuSans.ttf')
font_bold_path = os.path.join(current_dir, '..', 'static', 'fonts', 'DejaVuSans-Bold.ttf')

pdfmetrics.registerFont(TTFont('DejaVu', font_path))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_bold_path))


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
        fields = request.env['sonha.xac.nhan'].sudo().search([
            ('MODEL_ID.model', '=', model),
            ('REQUIRE_CONFIRM', '=', True),
        ])
        field_names = fields.mapped('FIELD_ID.name')
        return field_names

    def _safe(self, value, default=''):
        return value or default

    def _fmt_vn_date(self, d):
        if not d:
            return ''
        if isinstance(d, str):
            return d
        return f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}"

    @http.route('/download/phieu_nhap/<int:record_id>', type='http', auth='user')
    def download_pdf(self, record_id, **kwargs):
        record = request.env['nl.acc.ap.h'].browse(record_id)
        if not record.exists():
            return request.not_found()

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Logo tạm (user sẽ tự thay logo thật)
        logo_x = 20 * mm
        logo_y = height - 35 * mm
        p.setStrokeColor(colors.HexColor('#1f77b4'))
        p.setLineWidth(1)
        p.rect(logo_x, logo_y, 16 * mm, 16 * mm, stroke=1, fill=0)
        p.setFont('DejaVu-Bold', 11)
        p.setFillColor(colors.HexColor('#1f77b4'))
        p.drawCentredString(logo_x + 8 * mm, logo_y + 8 * mm - 4, 'LOGO')
        p.setFillColor(colors.black)

        p.setFont('DejaVu-Bold', 12)
        p.drawString(42 * mm, height - 20 * mm, self._safe(record.DVCS.name, 'CÔNG TY CỔ PHẦN [TÊN CÔNG TY]'))
        p.setFont('DejaVu', 10)
        p.drawString(42 * mm, height - 28 * mm, self._safe(record.DVCS.partner_id.contact_address, 'Địa chỉ: [ĐỊA CHỈ CÔNG TY]'))

        p.setFont('DejaVu-Bold', 11)
        p.drawRightString(width - 20 * mm, height - 20 * mm, 'Mẫu số 01 - VT')
        p.setFont('DejaVu', 10)
        p.drawRightString(width - 20 * mm, height - 28 * mm, '(Ban hành theo QĐ số 15/2006/QĐ-BTC)')

        p.setFont('DejaVu-Bold', 18)
        p.drawCentredString(width / 2, height - 45 * mm, 'PHIẾU NHẬP KHO')
        p.setFont('DejaVu', 14)
        p.drawCentredString(width / 2, height - 54 * mm, self._fmt_vn_date(record.NGAY_CT or date.today()))
        p.drawCentredString(width / 2, height - 62 * mm, f"Số: {self._safe(record.CHUNG_TU, f'PN/{record.id}')}")

        y = height - 78 * mm
        p.setFont('DejaVu', 13)
        p.drawString(20 * mm, y, f"Họ và tên người giao hàng: {self._safe(record.KHACH_HANG.TEN, '')}")
        y -= 10 * mm
        p.drawString(20 * mm, y, f"Theo hóa đơn số: {self._safe(record.SO_HD, '')}")
        p.drawRightString(width - 20 * mm, y, self._fmt_vn_date(record.NGAY_HD or record.NGAY_CT))
        y -= 10 * mm
        p.drawString(20 * mm, y, f"Nhập tại kho: {self._safe(record.KHO.TEN, '')}")
        y -= 10 * mm
        p.drawString(20 * mm, y, f"Nội dung: {self._safe(record.GHI_CHU, 'Phiếu nhập mua hàng')}")

        # Bảng chi tiết
        table_top = y - 8 * mm
        lines = record.ACC_SP_D
        data = [
            ['Stt', 'Tên, nhãn hiệu, quy cách,\nphẩm chất vật tư, dụng cụ\nsản phẩm hàng hóa', 'Mã vật tư', 'Đơn vị\ntính', 'Số lượng', '', 'Ghi chú'],
            ['', '', '', '', 'Theo chứng\ntừ', 'Thực nhập', ''],
        ]
        for idx, line in enumerate(lines, start=1):
            hh_name = line.HANG_HOA.TEN_HANG if hasattr(line.HANG_HOA, 'TEN_HANG') else line.HANG_HOA.TEN
            ma_hh = self._safe(getattr(line.HANG_HOA, 'MA_HANG', ''), '')
            dvt = self._safe(getattr(line.HANG_HOA, 'DVT', ''), '')
            data.append([
                str(idx),
                self._safe(hh_name, ''),
                ma_hh,
                dvt,
                str(line.SO_LUONG or ''),
                str(line.SO_LUONG2 or line.SO_LUONG or ''),
                ''
            ])

        if len(data) == 2:
            data.append(['1', '', '', '', '', '', ''])

        table = Table(data, colWidths=[10 * mm, 67 * mm, 30 * mm, 15 * mm, 22 * mm, 22 * mm, 32 * mm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
            ('SPAN', (0, 0), (0, 1)),
            ('SPAN', (1, 0), (1, 1)),
            ('SPAN', (2, 0), (2, 1)),
            ('SPAN', (3, 0), (3, 1)),
            ('SPAN', (4, 0), (5, 0)),
            ('SPAN', (6, 0), (6, 1)),
            ('FONTNAME', (0, 0), (-1, 1), 'DejaVu-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 8),
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 2), (-1, -1), 'DejaVu'),
            ('FONTSIZE', (0, 2), (-1, -1), 8),
            ('ALIGN', (0, 2), (0, -1), 'CENTER'),
            ('ALIGN', (2, 2), (6, -1), 'CENTER'),
            ('LEFTPADDING', (1, 2), (1, -1), 3),
            ('LINEABOVE', (0, 2), (-1, 2), 0.6, colors.black),
        ]))

        tw, th = table.wrapOn(p, width - 35 * mm, height)
        table.drawOn(p, 6 * mm, table_top - th)

        sign_y = table_top - th - 28 * mm
        p.setFont('DejaVu', 14)
        p.drawRightString(width - 20 * mm, sign_y + 16 * mm, self._fmt_vn_date(record.NGAY_CT or date.today()))

        p.setFont('DejaVu-Bold', 14)
        roles = ['Người lập phiếu', 'Quản đốc', 'Thủ kho', 'Kế toán trưởng']
        x_positions = [35 * mm, 85 * mm, 135 * mm, 185 * mm]
        for x, role in zip(x_positions, roles):
            p.drawCentredString(x, sign_y, role)
            p.setFont('DejaVu', 12)
            p.drawCentredString(x, sign_y - 8 * mm, '(Ký, họ tên)')
            p.setFont('DejaVu-Bold', 14)

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
