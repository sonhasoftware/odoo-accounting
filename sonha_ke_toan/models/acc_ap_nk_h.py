import datetime

from odoo import api, fields, models, exceptions, _, tools
import datetime
import logging
import re
import json

_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError


class AccApNkH(models.Model):
    _name = 'acc.ap.nk.h'
    _order = 'NGAY_CT DESC'
    _rec_name = 'CHUNG_TU'

    NGAY_CT = fields.Date(string="Ngày CT", store=True, default=lambda self: datetime.date.today())
    CHUNG_TU = fields.Char(string="Chứng từ", store=True, readonly=True, size=30)
    CTGS = fields.Char(string="CTGS", store=True, size=30)
    SO_HD = fields.Char(string="Số HĐ", store=True, size=10)
    SERI_HD = fields.Char(string="Seri HĐ", store=True, size=10)
    NGAY_HD = fields.Date(string="Ngày HĐ", store=True)
    MAU_SO = fields.Char(string="Mẫu số", store=True, size=10)
    PT_THUE = fields.Many2one('acc.thue', string="% Thuế", store=True)
    ONG_BA = fields.Char(string="Ông bà", store=True , size=60)
    GHI_CHU = fields.Char(string="Ghi chú", store=True, default="Phiếu nhập mua hàng", size=200)

    KHACH_HANG = fields.Many2one('acc.khach.hang', string="Khách hàng", store=True)
    KH_THUE = fields.Char(string="KH Thuế", store=True, size=150)
    MS_THUE = fields.Char(string="Mã số Thuế", store=True, size=20)
    DC_THUE = fields.Char(string="Địa chỉ Thuế", store=True, size=200)

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
        comodel_name="acc.ap.nk.d",
        inverse_name="ACC_AP_H",
        string="Bảng chi tiết",
        store=True
    )
    MENU_ID = fields.Many2one('ir.ui.menu', string="MENU", store=True)

    DG_THEO_TIEN = fields.Boolean("DG theo tiền", store=False)
    TOTAL_VAT = fields.Char("Tổng tiền, Tổng VAT, tổng SL", store=False, compute="_get_total_vat_sl_tien")
    KHACH_HANGC = fields.Many2one('acc.khach.hang', string="KH có", store=True)
    KHOC = fields.Many2one('acc.kho', string="Kho nhận", store=True)
    TINH = fields.Many2one('acc.tinh', string="Vùng", store=True)
    NGUON = fields.Many2one('acc.nguon', string="HTV Chuyển", store=True)
    LOAIDL = fields.Many2one('acc.loaidl', string="Loại DL", store=True)

    TSCD = fields.Many2one('acc.tscd', string="TSCĐ")

    @api.onchange('ACC_SP_D', 'ACC_SP_D.PS_NO1', 'ACC_SP_D.VAT', 'ACC_SP_D.SO_LUONG')
    def _get_total_vat_sl_tien(self):
        for r in self:
            lines = r.ACC_SP_D
            r.TOTAL_VAT = (
                f"Tổng tiền:{sum(lines.mapped('PS_NO1'))}, "
                f"VAT:{sum(lines.mapped('VAT'))}, "
                f"Tổng SL:{sum(lines.mapped('SO_LUONG'))}"
            )

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
        res = super(AccApNkH, self).default_get(fields_list)
        # Tìm phân quyền của user hiện tại
        permission = self.env['sonha.phan.quyen.nl'].sudo().search([
            ('MENU', '=', 378),
        ], limit=1)
        dl = self.env['acc.loaidl'].sudo().search([('id', '=', 5)])

        if permission:
            res.update({
                'BO_PHAN': permission.BO_PHAN.id or None,
                'KHO': permission.KHO.id or None,
                'KHOAN_MUC': permission.KHOAN_MUC.id or None,
                'VVIEC': permission.VVIEC.id or None,
                'CHI_NHANH': permission.CHI_NHANH.id or None,
                'TIEN_TE': permission.TIEN_TE.id or None,
                'MENU_ID': permission.MENU.id or 378,
                'MA_TK1_ID': permission.MA_TK1_ID.id or None,
                'LOAIDL': permission.LOAI_DL.id or dl.id,
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

            field_type = "TEXT"

            odoo_field = self._fields.get(key)
            if odoo_field:
                if isinstance(odoo_field, fields.Boolean):
                    field_type = "BOOLEAN"
                elif isinstance(odoo_field, fields.Integer):
                    field_type = "INTEGER"
                elif isinstance(odoo_field, (fields.Float, fields.Monetary)):
                    field_type = "DOUBLE PRECISION"
                elif isinstance(odoo_field, fields.Date):
                    field_type = "DATE"
                elif isinstance(odoo_field, fields.Datetime):
                    field_type = "TIMESTAMP"
                elif isinstance(odoo_field, fields.Many2one):
                    field_type = "BIGINT"  # 🔥 SỬA ĐÚNG
                elif isinstance(odoo_field, (fields.Char, fields.Text, fields.Selection)):
                    field_type = "TEXT"
                else:
                    field_type = "TEXT"
            else:
                # fallback theo giá trị
                if value is None:
                    field_type = "TEXT"
                elif isinstance(value, bool):
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

            cr.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" {field_type};')
            _logger.info(f"[AUTO] Created column {col} on {table_name} ({field_type})")
            existing_columns.add(col)

    # ==========================================================
    # 2️⃣ SAO LƯU DỮ LIỆU CHI TIẾT SANG BẢNG LOG
    # ==========================================================
    def _copy_to_tong_hop_abc(self, d_records):
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

        temp_rec = self.new(vals)
        vals_dict = {
            "HANG_HOA": None,
            "MA_TK0": "",
            "SO_LUONG": 0,
            "DON_GIA": 0,
            "PS_NO1": 0,
            "TIEN_NTE": 0,
            "VAT": 0,
            "NGAY_CT": str(temp_rec.NGAY_CT) or "",
            "CHUNG_TU": temp_rec.CHUNG_TU or "",
            "CTGS": temp_rec.CTGS or "",
            "SO_HD": temp_rec.SO_HD or "",
            "SERI_HD": temp_rec.SERI_HD or "",
            "NGAY_HD": str(temp_rec.NGAY_HD) or None,
            "MAU_SO": temp_rec.MAU_SO or None,
            "PT_THUE": temp_rec.PT_THUE.PT_THUE or "",
            "ONG_BA": temp_rec.ONG_BA or "",
            "GHI_CHU": temp_rec.GHI_CHU or "",
            "KHACH_HANG": temp_rec.KHACH_HANG.id or 0,
            "KH_THUE": temp_rec.KH_THUE or "",
            "MS_THUE": temp_rec.MS_THUE or "",
            "DC_THUE": temp_rec.DC_THUE or "",
            "BO_PHAN": temp_rec.BO_PHAN.id or 0,
            "VVIEC": temp_rec.VVIEC.id or 0,
            "KHO": temp_rec.KHO.id or 0,
            "KHOAN_MUC": temp_rec.KHOAN_MUC.id or 0,
            "TIEN_TE": temp_rec.TIEN_TE.id or "",
            "TY_GIA": temp_rec.TY_GIA or "",
            "MA_TK1": temp_rec.MA_TK1 or "",
            "DVCS": temp_rec.DVCS.id or 1,
            "CHI_NHANH": temp_rec.CHI_NHANH.id or 0,
            "MENU_ID": temp_rec.MENU_ID.id or 378,
            "NGUOI_TAO": self.env.uid or None,
            "NGUOI_SUA": self.env.uid or None,
        }
        table_name = 'acc.ap.nk.h'
        if len(temp_rec.ACC_SP_D) == 0:
            raise ValidationError("Không được phép để trống phần dữ liệu bên dưới!")

        for recs in temp_rec.ACC_SP_D:

            vals_dict.update({
                "HANG_HOA": recs.HANG_HOA.id or None,
                "MA_TK0": recs.MA_TK0 or "",
                "SO_LUONG": recs.SO_LUONG,
                "DON_GIA": recs.DON_GIA,
                "PS_NO1": recs.PS_NO1,
                "TIEN_NTE": recs.TIEN_NTE,
                "VAT": recs.VAT,
            })

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
        rec = super(AccApNkH, self).create(vals)
        query = "SELECT * FROM fn_chung_tu_tu_dong(%s, %s)"
        self.env.cr.execute(query, ('menu_378', str(rec.NGAY_CT)))
        rows = self.env.cr.fetchall()
        if rows:
            rec.CHUNG_TU = rows[0][0]

        return rec

    def _get_parent_value(self, record, vals, field_name):
        if field_name in vals:
            value = vals[field_name]
            field = record._fields[field_name]

            if field.type == 'many2one':
                return self.env[field.comodel_name].browse(value) if value else self.env[field.comodel_name]
            return value
        value = record[field_name]
        return value

    def read_to_vals(self, read_dict):
        vals = {}

        for key, val in read_dict.items():
            if key in {
                'id', 'display_name',
                'create_uid', 'create_date',
                'write_uid', 'write_date',
                '__last_update'
            }:
                continue
            if isinstance(val, tuple):
                vals[key] = val[0] if val else False
            elif val is None or val is False:
                vals[key] = False
            else:
                vals[key] = val

        return vals

    def write(self, vals):
        """Ghi dữ liệu acc.ap.h, sao lưu dữ liệu acc.ap.d sang bảng tổng hợp trước khi ghi."""

        for record in self:
            # Lấy D records từ vals hoặc D records hiện có
            if 'ACC_SP_D' in vals:
                # Nếu D records được edit từ form, lấy từ vals (dưới dạng (0, 0, {...}))
                new_d_records = vals.get('ACC_SP_D') or []

                # Chuyển đổi command format Odoo sang dict
                d_records_to_validate = []
                for cmd in new_d_records:
                    if cmd[0] == 0:  # Create command
                        d_records_to_validate.append(cmd[2])
                    elif cmd[0] == 1:  # Write command
                        # Lấy record và update với giá trị mới
                        d_record = self.env['acc.ap.nk.d'].browse(cmd[1])
                        read_data = d_record.read()[0]
                        d_dict = self.read_to_vals(read_data)
                        d_dict.update(cmd[2])
                        d_records_to_validate.append(d_dict)
            else:
                # Không có D records được edit, lấy D records hiện có
                all_d_records = self.env['acc.ap.nk.d'].search([('ACC_AP_H', '=', record.id)])
                d_records_to_validate = []
                for d in all_d_records:
                    read_data = d.read()[0]
                    d_vals = self.read_to_vals(read_data)
                    d_records_to_validate.append(d_vals)
            # VALIDATE từng D record

            vals_dict = {
                "HANG_HOA": None,
                "MA_TK0": "",
                "SO_LUONG": 0,
                "DON_GIA": 0,
                "PS_NO1": 0,
                "TIEN_NTE": 0,
                "VAT": 0,
                "NGAY_CT": str(self._get_parent_value(record, vals, 'NGAY_CT')) or "",
                "CHUNG_TU": self._get_parent_value(record, vals, 'CHUNG_TU') or "",
                "CTGS": self._get_parent_value(record, vals, 'CTGS') or "",
                "SO_HD": self._get_parent_value(record, vals, 'SO_HD') or "",
                "SERI_HD": self._get_parent_value(record, vals, 'SERI_HD') or "",
                "NGAY_HD": str(self._get_parent_value(record, vals, 'NGAY_HD')) or None,
                "MAU_SO": self._get_parent_value(record, vals, 'MAU_SO') or None,
                "PT_THUE": self._get_parent_value(record, vals, 'PT_THUE').PT_THUE or "",
                "ONG_BA": self._get_parent_value(record, vals, 'ONG_BA') or "",
                "GHI_CHU": self._get_parent_value(record, vals, 'GHI_CHU') or "",
                "KHACH_HANG": self._get_parent_value(record, vals, 'KHACH_HANG').id or 0,
                "KH_THUE": self._get_parent_value(record, vals, 'KH_THUE') or "",
                "MS_THUE": self._get_parent_value(record, vals, 'MS_THUE') or "",
                "DC_THUE": self._get_parent_value(record, vals, 'DC_THUE') or "",
                "BO_PHAN": self._get_parent_value(record, vals, 'BO_PHAN').id or 0,
                "VVIEC": self._get_parent_value(record, vals, 'VVIEC').id or 0,
                "KHO": self._get_parent_value(record, vals, 'KHO').id or 0,
                "KHOAN_MUC": self._get_parent_value(record, vals, 'KHOAN_MUC').id or 0,
                "TIEN_TE": self._get_parent_value(record, vals, 'TIEN_TE').id or "",
                "TY_GIA": self._get_parent_value(record, vals, 'TY_GIA') or "",
                "MA_TK1": self._get_parent_value(record, vals, 'MA_TK1_ID').MA or "",
                "DVCS": self._get_parent_value(record, vals, 'DVCS').id or 1,
                "CHI_NHANH": self._get_parent_value(record, vals, 'CHI_NHANH').id or 0,
                "MENU_ID": self._get_parent_value(record, vals, 'MENU_ID').id or 378,
                "NGUOI_TAO": self.create_uid.id or None,
                "NGUOI_SUA": self.env.uid or None,
            }

            table_name = 'acc.ap.nk.h'

            for d_vals in d_records_to_validate:
                ma_tk0 = self.env['acc.tai.khoan'].search([('id', '=', d_vals.get('MA_TK0_ID'))]).MA
                vals_dict.update({
                    "HANG_HOA": d_vals.get('HANG_HOA') or None,
                    "MA_TK0": ma_tk0 or "",
                    "SO_LUONG": d_vals.get('SO_LUONG'),
                    "DON_GIA": d_vals.get('DON_GIA'),
                    "PS_NO1": d_vals.get('PS_NO1'),
                    "TIEN_NTE": d_vals.get('TIEN_NTE'),
                    "VAT": d_vals.get('VAT'),
                })

                json_data = json.dumps(vals_dict)

                self.env.cr.execute(
                    """SELECT * FROM fn_check_nl(%s::text, %s::jsonb);""",
                    (table_name, json_data)
                )

                check = self.env.cr.dictfetchall()
                if check:
                    result = check[0]
                    loi = list(result.values())[0]
                    if loi:
                        raise ValidationError(loi)

        res = super(AccApNkH, self).write(vals)

        for record in self:
            all_d_records = self.env['acc.ap.nk.d'].search([('ACC_AP_H', '=', record.id)])
            if len(all_d_records) == 0:
                raise ValidationError("Không được phép để trống phần dữ liệu bên dưới!")

            # Copy D records sang bảng log
            self._copy_to_tong_hop_abc(all_d_records)

            # Chuẩn bị dữ liệu D
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

            self.env['nl.acc.tong.hop'].sudo().search([('ACC_NK_D', 'in', all_d_records.ids)]).unlink()
            self.env['acc.ap.nk.d'].sudo().search([('id', 'in', all_d_records.ids)]).unlink()

            if d_vals_list:
                self.env['acc.ap.nk.d'].sudo().create(d_vals_list)

        return res

    @api.onchange('TIEN_TE', 'TY_GIA')
    def _onchange_currency(self):
        for line in self.ACC_SP_D:
            line._onchange_tien_nte()

    @api.onchange('TY_GIA', 'DG_THEO_TIEN')
    def _onchange_thanh_tien(self):
        for line in self.ACC_SP_D:
            line.PS_NO1 = (line.SO_LUONG or 0) * (line.DON_GIA or 0) * (self.TY_GIA or 1)

    @api.onchange('PT_THUE')
    def _onchange_vat(self):
        for line in self.ACC_SP_D:
            line._onchange_vat()
