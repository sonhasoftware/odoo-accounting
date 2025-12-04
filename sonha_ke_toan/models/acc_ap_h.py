import datetime

from odoo import api, fields, models, exceptions, _, tools
import datetime
import logging
import re

_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError


class AccApH(models.Model):
    _name = 'nl.acc.ap.h'

    NGAY_CT = fields.Date(string="Ngày CT", store=True, default=lambda self: datetime.date.today())
    CHUNG_TU = fields.Char(string="Chứng từ", store=True, readonly=True)
    CTGS = fields.Char(string="CTGS", store=True)
    SO_HD = fields.Char(string="Số HĐ", store=True)
    SERI_HD = fields.Char(string="Seri HĐ", store=True)
    NGAY_HD = fields.Date(string="Ngày HĐ", store=True)
    MAU_SO = fields.Char(string="Mẫu số", store=True)
    PT_THUE = fields.Many2one('acc.thue', string="% Thuế", store=True)
    ONG_BA = fields.Char(string="Ông bà", store=True)
    GHI_CHU = fields.Char(string="Ghi chú", store=True, default="Phiếu nhập mua hàng")

    KHACH_HANG = fields.Many2one('acc.khach.hang', string="Khách hàng", store=True)
    KH_THUE = fields.Char(string="KH Thuế", store=True)
    MS_THUE = fields.Char(string="Mã số Thuế", store=True)
    DC_THUE = fields.Char(string="Địa chỉ Thuế", store=True)

    BO_PHAN = fields.Many2one('acc.bo.phan', string="Bộ phận", store=True)

    # Liên kết đến bảng vụ việc (hợp đồng)
    VVIEC = fields.Many2one('acc.vviec', string="Vụ việc", store=True)

    # Liên kết đến bảng kho
    KHO = fields.Many2one('acc.kho', string="Kho", store=True)

    # Khoản mục (nếu là bảng riêng thì có thể Many2one)
    KHOAN_MUC = fields.Many2one('acc.khoan.muc', string="Khoản mục", store=True)

    TIEN_TE = fields.Many2one('acc.tien.te', string="Tiền tệ", store=True)
    TY_GIA = fields.Float(string="Tỷ giá", store=True, default=1)

    # Liên kết đến bảng tài khoản
    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True, domain=lambda self: self._get_domain_tai_khoan())
    MA_TK1 = fields.Char(related='MA_TK1_ID.MA', string="Có", store=True)

    # Liên kết đến bảng đơn vị cơ sở (DVCS)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)

    # Liên kết đến bảng chi nhánh
    CHI_NHANH = fields.Many2one('acc.chi.nhanh', string="Chi nhánh", store=True)

    ACC_SP_D = fields.One2many(
        comodel_name="nl.acc.ap.d",
        inverse_name="ACC_AP_H",
        string="Bảng chi tiết",
        store=True
    )
    MENU_ID = fields.Many2one('ir.ui.menu', string="MENU", store=True)

    DG_THEO_TIEN = fields.Boolean("DG theo tiền", store=False)
    TOTAL_VAT = fields.Char("Tổng tiền, Tổng VAT, tổng SL", store=False, compute="_get_total_vat_sl_tien")

    def _get_total_vat_sl_tien(self):
        for r in self:
            list_total = self.env['nl.acc.ap.d'].sudo().search([('ACC_AP_H', '=', r.id)])
            tt = sum(list_total.mapped('PS_NO1')) or 0
            vat = sum(list_total.mapped('VAT')) or 0
            sl = sum(list_total.mapped('SO_LUONG')) or 0

            r.TOTAL_VAT = f"Tổng tiền:{tt}, VAT:{vat}, Tổng SL:{sl}"

    @api.model
    def _get_domain_tai_khoan(self):
        """
        Domain động cho field MA_TK0_ID dựa trên dữ liệu trả về từ function PostgreSQL.
        """
        company_id = self.env.company.id

        query = "SELECT * FROM public.fn_acc_tai_khoan_nl(%s)"
        self.env.cr.execute(query, (company_id,))
        rows = self.env.cr.fetchall()

        ids = [r[0] for r in rows if r and r[0]]
        if not ids:
            return [('id', '=', 0)]

        return [('id', 'in', ids)]

    def default_get(self, fields_list):
        """
        Tự động lấy các giá trị mặc định từ bảng phân quyền acc.phan.quyen
        dựa theo người dùng đang đăng nhập.
        """
        res = super(AccApH, self).default_get(fields_list)
        current_user = self.env.user
        company_id = self.env.company

        # Tìm phân quyền của user hiện tại
        permission = self.env['sonha.phan.quyen.nl'].sudo().search([
            ('MENU', '=', 337),
        ], limit=1)

        if permission:
            res.update({
                'BO_PHAN': permission.BO_PHAN.id or None,
                'KHO': permission.KHO.id or None,
                'KHOAN_MUC': permission.KHOAN_MUC.id or None,
                'VVIEC': permission.VVIEC.id or None,
                'CHI_NHANH': permission.CHI_NHANH.id or None,
                'DVCS': permission.DVCS.id or None,
                'TIEN_TE': permission.TIEN_TE.id or None,
                'MENU_ID': permission.MENU.id or None,
                'MA_TK1_ID': permission.MA_TK1_ID.id or None,
            })

        return res

    def create_dynamic_fields(self, table_name, data_dict):
        """Tự động tạo cột đúng định dạng theo kiểu dữ liệu Odoo."""
        cr = self._cr
        cr.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s;
        """, (table_name.lower(),))
        existing_columns = {row[0].upper() for row in cr.fetchall()}

        for key, value in data_dict.items():
            col = key.upper()
            if col in existing_columns:
                continue

            # --- Xác định kiểu dữ liệu theo định nghĩa field ---
            field_type = "TEXT"
            if key in self._fields:
                odoo_field = self._fields[key]
                t = type(odoo_field)
                if isinstance(odoo_field, fields.Boolean):
                    field_type = "BOOLEAN"
                elif isinstance(odoo_field, fields.Integer):
                    field_type = "INTEGER"
                elif isinstance(odoo_field, fields.Float):
                    field_type = "DOUBLE PRECISION"
                elif isinstance(odoo_field, fields.Monetary):
                    field_type = "DOUBLE PRECISION"
                elif isinstance(odoo_field, fields.Date):
                    field_type = "DATE"
                elif isinstance(odoo_field, fields.Datetime):
                    field_type = "TIMESTAMP"
                elif isinstance(odoo_field, (fields.Char, fields.Text, fields.Selection, fields.Many2one)):
                    field_type = "TEXT"
                else:
                    field_type = "TEXT"
            else:
                # fallback nếu không nằm trong _fields
                if isinstance(value, bool):
                    field_type = "BOOLEAN"
                elif isinstance(value, int):
                    field_type = "INTEGER"
                elif isinstance(value, float):
                    field_type = "DOUBLE PRECISION"
                elif isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
                    field_type = "DATE"
                elif isinstance(value, datetime.datetime):
                    field_type = "TIMESTAMP"
                else:
                    field_type = "TEXT"

            # --- Tạo cột mới ---
            try:
                cr.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" {field_type};')
                _logger.info(f"[AUTO] Created column {col} on {table_name} ({field_type})")
                existing_columns.add(col)
            except Exception as e:
                _logger.error(f"[ERROR] Cannot add column {col}: {e}")

        cr.commit()

    # ==========================================================
    # 2️⃣ SAO LƯU DỮ LIỆU CHI TIẾT SANG BẢNG LOG
    # ==========================================================
    def _copy_to_tong_hop_abc(self, d_records):
        """Sao lưu dữ liệu nl.acc.ap.d sang bảng nl_acc_tong_hop_log với đúng định dạng."""
        if not d_records:
            return

        table_name = "nl_acc_tong_hop_log"
        cr = self._cr
        skip_fields = {
            'id', '__last_update', 'display_name',
            'create_uid', 'write_uid', 'create_date', 'write_date'
        }

        for rec in d_records:
            data = {}

            for fld_name, field in rec._fields.items():
                # ⚠️ Bỏ qua các trường không cần lưu
                if fld_name in skip_fields or not field.store:
                    continue

                val = getattr(rec, fld_name)

                # ✅ Convert kiểu dữ liệu an toàn
                if field.type == 'many2one':
                    val = val.id if val else None
                elif field.type in ['one2many', 'many2many']:
                    val = ','.join(str(v) for v in val.ids) if val else None
                elif isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
                    val = val
                elif isinstance(val, datetime.datetime):
                    val = val
                elif isinstance(val, bool):
                    val = bool(val)
                elif isinstance(val, (int, float, str)):
                    pass
                elif val is None:
                    pass
                else:
                    val = str(val)

                data[fld_name.upper()] = val

            if not data:
                continue

            # 🔨 Tạo cột nếu chưa có
            self.create_dynamic_fields(table_name, data)

            # 🧱 Build SQL insert
            cols = [f'"{k}"' for k in data.keys()]
            placeholders = ', '.join(['%s'] * len(data))
            values = list(data.values())

            sql = f'INSERT INTO "{table_name}" ({", ".join(cols)}) VALUES ({placeholders});'
            try:
                cr.execute(sql, values)
            except Exception as e:
                _logger.error(f"[ERROR] Insert failed for record {rec.id}: {e}\nData: {data}")
                raise

        cr.commit()
        _logger.info(f"[AUTO] Inserted {len(d_records)} rows into {table_name}")

    # ==========================================================
    # 3️⃣ GHI DỮ LIỆU HEADER + SAO LƯU LOG
    # ==========================================================
    def create(self, vals):
        rec = super(AccApH, self).create(vals)

        # Gọi function sinh chứng từ tự động
        query = "SELECT * FROM fn_chung_tu_tu_dong(%s, %s)"
        self.env.cr.execute(query, ('menu_337', str(rec.NGAY_CT)))
        rows = self.env.cr.fetchall()
        if rows:
            rec.CHUNG_TU = rows[0][0]

        return rec

    def write(self, vals):
        """Ghi dữ liệu acc.ap.h, sao lưu dữ liệu acc.ap.d sang bảng tổng hợp trước khi ghi."""
        res = super(AccApH, self).write(vals)

        for record in self:
            all_d_records = self.env['nl.acc.ap.d'].search([('ACC_AP_H', '=', record.id)])

            # 1️⃣ Sao lưu dữ liệu D sang bảng tổng hợp log
            self._copy_to_tong_hop_abc(all_d_records)

            # 2️⃣ Chuẩn bị dữ liệu H và D để tạo lại (convert đúng kiểu)
            vals_h = {}
            for field_name, field in record._fields.items():
                if field_name in ['id', '__last_update', 'line_ids', 'create_date', 'write_date', 'create_uid', 'write_uid']:
                    continue
                value = record[field_name]
                if field.type == 'many2one':
                    vals_h[field_name] = value.id if value else False
                elif field.type in ['one2many', 'many2many']:
                    continue
                else:
                    vals_h[field_name] = value

            d_vals_list = []
            for d in all_d_records:
                vals_d = {}
                for field_name, field in d._fields.items():
                    if field_name in ['id', '__last_update', 'create_date', 'write_date', 'create_uid', 'write_uid']:
                        continue
                    value = d[field_name]
                    if field.type == 'many2one':
                        vals_d[field_name] = value.id if value else False
                    elif field.type in ['one2many', 'many2many']:
                        continue
                    else:
                        vals_d[field_name] = value
                d_vals_list.append(vals_d)

            self.env['nl.acc.tong.hop'].sudo().search([('ACC_AP_D', 'in', all_d_records.ids)]).unlink()

            # 3️⃣ Tạo lại bản ghi H & D (sau khi backup)
            new_h = super(AccApH, self).create(vals_h)
            if new_h and d_vals_list:
                for d_val in d_vals_list:
                    d_val['ACC_AP_H'] = new_h.id
                self.env['nl.acc.ap.d'].sudo().create(d_vals_list)

            record.sudo().unlink()
            all_d_records.sudo().unlink()

            self.action_return(new_h)

    def action_return(self, new_h):

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env.ref('sonha_ke_toan.menu_nl_acc_ap_h').id
        action_id = self.env.ref('sonha_ke_toan.acc_nl_ap_h_action').id

        url = (
                f"{base_url}/web#id={new_h.id}"
                f"&model=nl.acc.ap.h"
                f"&view_type=form"
                f"&menu_id={menu_id}"
                f"&action={action_id}"
            )

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }