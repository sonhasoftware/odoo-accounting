import datetime

from odoo import api, fields, models, exceptions, _, tools
import datetime
import logging
import re
import json

_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError


class AccApH(models.Model):
    _name = 'nl.acc.ap.h'
    _order = 'NGAY_CT DESC'
    _rec_name = 'CHUNG_TU'

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
    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True)
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

    @api.onchange('ACC_SP_D')
    def _get_total_vat_sl_tien(self):
        for r in self:
            list_total = self.env['nl.acc.ap.d'].sudo().search([('ACC_AP_H', '=', r.id)])
            tt = sum(list_total.mapped('PS_NO1')) or 0
            vat = sum(list_total.mapped('VAT')) or 0
            sl = sum(list_total.mapped('SO_LUONG')) or 0

            r.TOTAL_VAT = f"Tổng tiền:{tt}, VAT:{vat}, Tổng SL:{sl}"

    # @api.model
    # def _get_domain_tai_khoan(self):
    #     """
    #     Domain động cho field MA_TK0_ID dựa trên dữ liệu trả về từ function PostgreSQL.
    #     """
    #     company_id = self.env.company.id
    #
    #     query = "SELECT * FROM public.fn_acc_tai_khoan_nl(%s)"
    #     self.env.cr.execute(query, (company_id,))
    #     rows = self.env.cr.fetchall()
    #
    #     ids = [r[0] for r in rows if r and r[0]]
    #     if not ids:
    #         return [('id', '=', 0)]
    #
    #     return [('id', 'in', ids)]

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
                if fld_name in skip_fields or not field.store:
                    continue

                val = getattr(rec, fld_name)

                # 🛠 Convert dữ liệu an toàn
                if val is False:
                    val = None

                if field.type == 'many2one':
                    val = val.id if val else None

                elif field.type in ['one2many', 'many2many']:
                    val = ','.join(map(str, val.ids)) if val else None

                elif field.type == 'date':
                    val = val.isoformat() if val else None  # 🟢 CHỈNH QUAN TRỌNG

                elif field.type == 'datetime':
                    val = val.strftime('%Y-%m-%d %H:%M:%S') if val else None  # 🟢 QUAN TRỌNG

                elif field.type == 'boolean':
                    val = bool(val) if val is not None else None

                elif field.type in ['float', 'integer', 'char', 'text']:
                    pass  # giữ nguyên

                elif val is None:
                    pass

                else:
                    val = str(val)

                data[fld_name.upper()] = val

            if not data:
                continue

            # 🔨 Tạo cột nếu chưa có
            self.create_dynamic_fields(table_name, data)

            # INSERT
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

        for recs in rec.ACC_SP_D:

            vals_dict = {
                "HANG_HOA": recs.HANG_HOA.id or None,
                "MA_TK0": recs.MA_TK0 or "",
                "SO_LUONG": recs.SO_LUONG,
                "DON_GIA": recs.DON_GIA,
                "PS_NO1": recs.PS_NO1,
                "TIEN_NTE": recs.TIEN_NTE,
                "VAT": recs.VAT,
                "NGAY_CT": str(rec.NGAY_CT) or "",
                "CHUNG_TU": rec.CHUNG_TU or "",
                "CTGS": rec.CTGS or "",
                "SO_HD": rec.SO_HD or "",
                "SERI_HD": rec.SERI_HD or "",
                "NGAY_HD": str(rec.NGAY_HD) or None,
                "MAU_SO": rec.MAU_SO or None,
                "PT_THUE": rec.PT_THUE.PT_THUE or "",
                "ONG_BA": rec.ONG_BA or "",
                "GHI_CHU": rec.GHI_CHU or "",
                "KHACH_HANG": rec.KHACH_HANG.id or 0,
                "KH_THUE": rec.KH_THUE or "",
                "MS_THUE": rec.MS_THUE or "",
                "DC_THUE": rec.DC_THUE or "",
                "BO_PHAN": rec.BO_PHAN.id or 0,
                "VVIEC": rec.VVIEC.id or 0,
                "KHO": rec.KHO.id or 0,
                "KHOAN_MUC": rec.KHOAN_MUC.id or 0,
                "TIEN_TE": rec.TIEN_TE.id or "",
                "TY_GIA": rec.TY_GIA or "",
                "MA_TK1": rec.MA_TK1 or "",
                "DVCS": rec.DVCS.id or 1,
                "CHI_NHANH": rec.CHI_NHANH.id or 0,
                "MENU_ID": rec.MENU_ID.id or 337,
                "NGUOI_TAO": self.env.uid or None,
                "NGUOI_SUA": self.env.uid or None,
            }

            table_name = 'nl.acc.ap.h'

            json_data = json.dumps(vals_dict)

            self.env.cr.execute("""SELECT * FROM fn_check_nl(%s::text, %s::jsonb);""", (table_name, json_data))
            check = self.env.cr.dictfetchall()
            if check:
                result = check[0]
                loi = list(result.values())[0]
                if loi == None:
                    pass
                else:
                    raise ValidationError(loi)

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
            for recs in record.ACC_SP_D:

                vals_dict = {
                    "HANG_HOA": recs.HANG_HOA.id or None,
                    "MA_TK0": recs.MA_TK0 or "",
                    "SO_LUONG": recs.SO_LUONG,
                    "DON_GIA": recs.DON_GIA,
                    "PS_NO1": recs.PS_NO1,
                    "TIEN_NTE": recs.TIEN_NTE,
                    "VAT": recs.VAT,
                    "NGAY_CT": str(record.NGAY_CT) or "",
                    "CHUNG_TU": record.CHUNG_TU or "",
                    "CTGS": record.CTGS or "",
                    "SO_HD": record.SO_HD or "",
                    "SERI_HD": record.SERI_HD or "",
                    "NGAY_HD": str(record.NGAY_HD) or None,
                    "MAU_SO": record.MAU_SO or None,
                    "PT_THUE": record.PT_THUE.PT_THUE or "",
                    "ONG_BA": record.ONG_BA or "",
                    "GHI_CHU": record.GHI_CHU or "",
                    "KHACH_HANG": record.KHACH_HANG.id or 0,
                    "KH_THUE": record.KH_THUE or "",
                    "MS_THUE": record.MS_THUE or "",
                    "DC_THUE": record.DC_THUE or "",
                    "BO_PHAN": record.BO_PHAN.id or 0,
                    "VVIEC": record.VVIEC.id or 0,
                    "KHO": record.KHO.id or 0,
                    "KHOAN_MUC": record.KHOAN_MUC.id or 0,
                    "TIEN_TE": record.TIEN_TE.id or "",
                    "TY_GIA": record.TY_GIA or "",
                    "MA_TK1": record.MA_TK1 or "",
                    "DVCS": record.DVCS.id or 1,
                    "CHI_NHANH": record.CHI_NHANH.id or 0,
                    "MENU_ID": record.MENU_ID.id or 337,
                    "NGUOI_TAO": self.create_uid.id or None,
                    "NGUOI_SUA": self.env.uid or None,
                }

                table_name = 'nl.acc.ap.h'

                json_data = json.dumps(vals_dict)
                self.env.cr.execute("""SELECT * FROM fn_check_nl(%s::text, %s::jsonb);""", (table_name, json_data))
                check = self.env.cr.dictfetchall()
                if check:
                    result = check[0]
                    loi = list(result.values())[0]
                    if loi == None:
                        pass
                    else:
                        raise ValidationError(loi)
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
            self.env['nl.acc.ap.d'].sudo().search([('id', 'in', all_d_records.ids)]).unlink()

            if d_vals_list:
                self.env['nl.acc.ap.d'].sudo().create(d_vals_list)



    # def action_return(self, new_h):
    #
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     menu_id = self.env.ref('sonha_ke_toan.menu_nl_acc_ap_h').id
    #     action_id = self.env.ref('sonha_ke_toan.acc_nl_ap_h_action').id
    #
    #     # url = (
    #     #         f"{base_url}/web#action={action_id}"
    #     #         f"&model=nl.acc.ap.h"
    #     #         f"&view_type=list"
    #     #         f"&cids={1-2}"
    #     #         f"&menu_id={menu_id}"
    #     #     )
    #
    #     url = f"{base_url}/web#action={action_id}&model=nl.acc.ap.h&&view_type=list&menu_id={menu_id}"
    #
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': url,
    #         'target': 'self',
    #     }
    #
    # def _validate_record_lines(self, rec):
    #     """Validate từng dòng ACC_SP_D của rec bằng fn_check_nl.
    #     Nếu có lỗi sẽ raise ValidationError với message từ DB function."""
    #     table_name = 'nl.acc.ap.h'
    #     for line in rec.ACC_SP_D:
    #         vals_dict = {
    #             "HANG_HOA": line.HANG_HOA.id or None,
    #             "MA_TK0": line.MA_TK0 or "",
    #             "SO_LUONG": line.SO_LUONG,
    #             "DON_GIA": line.DON_GIA,
    #             "PS_NO1": line.PS_NO1,
    #             "TIEN_NTE": line.TIEN_NTE,
    #             "VAT": line.VAT,
    #             "NGAY_CT": str(rec.NGAY_CT) or "",
    #             "CHUNG_TU": rec.CHUNG_TU or "",
    #             "CTGS": rec.CTGS or "",
    #             "SO_HD": rec.SO_HD or "",
    #             "SERI_HD": rec.SERI_HD or "",
    #             "NGAY_HD": str(rec.NGAY_HD) or None,
    #             "MAU_SO": rec.MAU_SO or None,
    #             "PT_THUE": rec.PT_THUE.PT_THUE or "",
    #             "ONG_BA": rec.ONG_BA or "",
    #             "GHI_CHU": rec.GHI_CHU or "",
    #             "KHACH_HANG": rec.KHACH_HANG.id or 0,
    #             "KH_THUE": rec.KH_THUE or "",
    #             "MS_THUE": rec.MS_THUE or "",
    #             "DC_THUE": rec.DC_THUE or "",
    #             "BO_PHAN": rec.BO_PHAN.id or 0,
    #             "VVIEC": rec.VVIEC.id or 0,
    #             "KHO": rec.KHO.id or 0,
    #             "KHOAN_MUC": rec.KHOAN_MUC.id or 0,
    #             "TIEN_TE": rec.TIEN_TE.id or "",
    #             "TY_GIA": rec.TY_GIA or "",
    #             "MA_TK1": rec.MA_TK1 or "",
    #             "DVCS": rec.DVCS.id or 1,
    #             "CHI_NHANH": rec.CHI_NHANH.id or 0,
    #             "MENU_ID": rec.MENU_ID.id or 337,
    #         }
    #         json_data = json.dumps(vals_dict)
    #         self.env.cr.execute("""SELECT * FROM fn_check_nl(%s::text, %s::jsonb);""", (table_name, json_data))
    #         check = self.env.cr.dictfetchall()
    #         if check:
    #             result = check[0]
    #             loi = list(result.values())[0]
    #             if loi == None:
    #                 pass
    #             else:
    #                 raise ValidationError(loi)
    #
    # # HÀM GỌI CHỨNG TỪ TỰ ĐỘNG (dùng cho create)
    # def _generate_chung_tu(self, menu_key, ngay_ct):
    #     """Gọi fn_chung_tu_tu_dong để tạo CHUNG_TU. Trả về chuỗi hoặc False."""
    #     query = "SELECT * FROM fn_chung_tu_tu_dong(%s, %s)"
    #     self.env.cr.execute(query, (menu_key, str(ngay_ct)))
    #     rows = self.env.cr.fetchall()
    #     if rows:
    #         return rows[0][0]
    #     return False
    #
    # # HÀM PHỤ: sao lưu D sang bảng tổng hợp (giữ nguyên gọi hàm bạn đã viết)
    #
    # # HÀM NÚT CHÍNH: gọi khi nhấn nút
    # def action_custom_save(self):
    #     """Nút Lưu & Xử lý: - nếu record mới => create logic
    #                                     - nếu record có id => chạy logic chỉnh sửa (như trong write của bạn)."""
    #     self.ensure_one()
    #
    #     mode = self.form_initial_mode or self.env.context.get('form_view_initial_mode') or self.env.context.get('mode')
    #
    #     # Nếu chưa có id (bản ghi chưa được tạo trong DB) -> tạo mới
    #     if not self._origin.id:
    #         # LƯU record trước (tạo mới) bằng cách chuyển attrs hiện tại thành dict:
    #         # Odoo thường auto save trước khi gọi object button, nhưng để an toàn ta chuẩn bị vals.
    #         vals_for_create = {}
    #         for field_name, field in self._fields.items():
    #             if field_name in ['id', '__last_update', 'create_date', 'write_date', 'create_uid', 'write_uid']:
    #                 continue
    #             # lấy giá trị hiện tại trên form
    #             value = self[field_name]
    #             if field.type == 'many2one':
    #                 vals_for_create[field_name] = value.id if value else False
    #             elif field.type in ['one2many', 'many2many']:
    #                 # one2many/many2many trên form cần được truyền đặc biệt; để đơn giản ta skip
    #                 # vì create sẽ lấy ACC_SP_D từ cache khi super create được gọi bằng framework.
    #                 continue
    #             else:
    #                 vals_for_create[field_name] = value
    #
    #         # Tạo bản ghi bằng super để không gọi lại logic create override của bạn (nếu muốn bypass thì dùng super)
    #         rec = super(AccApH, self).create(vals_for_create)
    #
    #         # Validate từng dòng mới
    #         # self._validate_record_lines(rec)
    #
    #         # Gọi function sinh chứng từ tự động (ví dụ menu_337)
    #         chung_tu = self._generate_chung_tu('menu_337', rec.NGAY_CT)
    #         if chung_tu:
    #             rec.CHUNG_TU = chung_tu
    #
    #         return rec
    #
    #     # Nếu đã có id -> đang chỉnh sửa: áp dụng logic write của bạn
    #     else:
    #         # Lưu những thay đổi hiện tại trước (đảm bảo write được persist)
    #         # Gọi write với {} sẽ không làm thay đổi nhưng sẽ persist các giá trị trên form nếu cần.
    #         self.write({})
    #
    #         for record in self:
    #             # 1) Validate từng dòng
    #             # self._validate_record_lines(record)
    #
    #             chung_tu = self._generate_chung_tu('menu_337', record.NGAY_CT)
    #             if chung_tu:
    #                 record.CHUNG_TU = chung_tu
    #
    #             # 2) Lấy tất cả bản ghi D liên quan
    #             all_d_records = self.env['nl.acc.ap.d'].search([('ACC_AP_H', '=', record.id)])
    #
    #             self._copy_to_tong_hop_abc(all_d_records)
    #
    #             # 4) Chuẩn bị dữ liệu H để tạo lại (convert đúng kiểu như bạn viết)
    #             vals_h = {}
    #             for field_name, field in record._fields.items():
    #                 if field_name in ['id', '__last_update', 'line_ids', 'create_date', 'write_date', 'create_uid', 'write_uid']:
    #                     continue
    #                 value = record[field_name]
    #                 if field.type == 'many2one':
    #                     vals_h[field_name] = value.id if value else False
    #                 elif field.type in ['one2many', 'many2many']:
    #                     continue
    #                 else:
    #                     vals_h[field_name] = value
    #
    #             # 5) Chuẩn bị dữ liệu D (list)
    #             d_vals_list = []
    #             for d in all_d_records:
    #                 vals_d = {}
    #                 for field_name, field in d._fields.items():
    #                     if field_name in ['id', '__last_update', 'create_date', 'write_date', 'create_uid', 'write_uid']:
    #                         continue
    #                     value = d[field_name]
    #                     if field.type == 'many2one':
    #                         vals_d[field_name] = value.id if value else False
    #                     elif field.type in ['one2many', 'many2many']:
    #                         continue
    #                     else:
    #                         vals_d[field_name] = value
    #                 d_vals_list.append(vals_d)
    #
    #             # 6) Xóa record tổng hợp cũ liên quan đến these D nếu có
    #             self.env['nl.acc.tong.hop'].sudo().search([('ACC_AP_D', 'in', all_d_records.ids)]).unlink()
    #
    #             # 7) Tạo lại bản ghi H & D (sau khi backup)
    #             new_h = super(AccApH, self).create(vals_h)
    #             if new_h and d_vals_list:
    #                 for d_val in d_vals_list:
    #                     d_val['ACC_AP_H'] = new_h.id
    #                 # tạo D mới bằng sudo (giả sử cần quyền)
    #                 self.env['nl.acc.ap.d'].sudo().create(d_vals_list)
    #
    #             # 8) Xóa bản ghi cũ và D cũ
    #             try:
    #                 record.sudo().unlink()
    #             except Exception:
    #                 # nếu unlink thất bại, raise để rollback
    #                 raise ValidationError("Đang có vấn đề về bản ghi, vui lòng kiểm tra lại!")
    #
    #             try:
    #                 all_d_records.sudo().unlink()
    #             except Exception:
    #                 # nếu unlink thất bại, raise để rollback
    #                 raise ValidationError("Đang có vấn đề về bản ghi con, vui lòng kiểm tra lại!")
    #
    #             return self.action_return(new_h)

