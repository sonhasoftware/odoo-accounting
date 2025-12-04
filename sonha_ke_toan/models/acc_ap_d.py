from odoo import api, fields, models, exceptions, _
import datetime
import re
import logging
import json

_logger = logging.getLogger(__name__)

# from odoo.exceptions import ValidationError


class AccApD(models.Model):
    _name = 'nl.acc.ap.d'

    ACC_AP_H = fields.Many2one('nl.acc.ap.h', string="ID Header", store=True)

    MA_TK0_ID = fields.Many2one('acc.tai.khoan', string="Nợ", store=True, compute='get_ma_tk_id', readonly=False)
    MA_TK0 = fields.Char(related='MA_TK0_ID.MA', string="Nợ", store=True)

    HANG_HOA = fields.Many2one('acc.hang.hoa', string="Hàng hóa", store=True)

    SO_LUONG = fields.Float("SL", store=True)
    DON_GIA = fields.Float("Đơn giá", store=True)
    PS_NO1 = fields.Integer("Thành tiền", store=True, compute="_get_ps_no1")
    TIEN_NTE = fields.Float("Ngoại tệ", store=True, compute="_get_tien_nte")
    VAT = fields.Float("Vat", store=True, compute="_get_vat")

    # field theo header
    NGAY_CT = fields.Date(string="Ngày CT", store=True)
    CHUNG_TU = fields.Char(string="Chứng từ", store=True)
    CTGS = fields.Char(string="CTGS", store=True)
    SO_HD = fields.Char(string="Số HĐ", store=True)
    SERI_HD = fields.Char(string="Seri HĐ", store=True)
    NGAY_HD = fields.Date(string="Ngày HĐ", store=True)
    MAU_SO = fields.Char(string="Mẫu số", store=True)
    PT_THUE = fields.Many2one('acc.thue', string="% Thuế", store=True)
    ONG_BA = fields.Char(string="Ông bà", store=True)
    GHI_CHU = fields.Char(string="Ghi chú", store=True)

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
    TY_GIA = fields.Float(string="Tỷ giá", store=True)

    # Liên kết đến bảng tài khoản
    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True)
    MA_TK1 = fields.Char(related='MA_TK1_ID.MA', string="Có", store=True)

    # Liên kết đến bảng đơn vị cơ sở (DVCS)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)

    # Liên kết đến bảng chi nhánh
    CHI_NHANH = fields.Many2one('acc.chi.nhanh', string="Chi nhánh", store=True)
    MENU_ID = fields.Many2one('ir.ui.menu', string="MENU", store=True)

    @api.onchange('DON_GIA')
    def _onchange_don_gia(self):
        permission = self.env['sonha.phan.quyen.nl'].sudo().search([
            ('MENU', '=', 337),
        ], limit=1)
        for r in self:
            if permission.GIA_MUA:
                don_gia = self.env['acc.gia.mua'].sudo().search([('HANG_HOA', '=', r.HANG_HOA.id),
                                                                 ('NGAY_HL', '<=', r.NGAY_CT)], order='NGAY_HL desc', limit=1)
                if don_gia and don_gia.DON_GIA:
                    r.DON_GIA = don_gia.DON_GIA
                else:
                    pass
            else:
                pass

    @api.onchange('HANG_HOA')
    @api.depends('HANG_HOA')
    def get_ma_tk_id(self):
        for r in self:
            if r.HANG_HOA and r.HANG_HOA.TK_KHO_ID:
                r.MA_TK0_ID = r.HANG_HOA.TK_KHO_ID.id
            else:
                pass

    @api.onchange('SO_LUONG', 'DON_GIA')
    @api.depends('SO_LUONG', 'DON_GIA')
    def _get_tien_nte(self):
        pass
        # for r in self:
        #     if r.TIEN_TE.MA != "VND":
        #         r.TIEN_NTE = r.SO_LUONG * r.DON_GIA
        #     else:
        #         pass

    @api.onchange('SO_LUONG', 'DON_GIA', 'ACC_AP_H.TY_GIA')
    @api.depends('SO_LUONG', 'DON_GIA', 'ACC_AP_H.TY_GIA')
    def _get_ps_no1(self):
        for r in self:
            r.PS_NO1 = r.SO_LUONG * r.DON_GIA * r.ACC_AP_H.TY_GIA

    @api.onchange('PS_NO1', 'ACC_AP_H.PT_THUE')
    @api.depends('PS_NO1', 'ACC_AP_H.PT_THUE')
    def _get_vat(self):
        for r in self:
            r.VAT = r.PS_NO1 * (r.ACC_AP_H.PT_THUE.PT_THUE / 100)

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

    @api.model
    def create(self, vals):
        # --- Merge dữ liệu header nếu có ---
        if vals.get('ACC_AP_H'):
            related = self.env['nl.acc.ap.h'].sudo().browse(vals['ACC_AP_H'])
            if related.exists():
                vals.update({
                    'NGAY_CT': related.NGAY_CT,
                    'CHUNG_TU': related.CHUNG_TU,
                    'CTGS': related.CTGS,
                    'SO_HD': related.SO_HD,
                    'SERI_HD': related.SERI_HD,
                    'NGAY_HD': related.NGAY_HD,
                    'MAU_SO': related.MAU_SO,
                    'PT_THUE': related.PT_THUE.id if related.PT_THUE else False,
                    'ONG_BA': related.ONG_BA,
                    'GHI_CHU': related.GHI_CHU,
                    'KHACH_HANG': related.KHACH_HANG.id if related.KHACH_HANG else False,
                    'KH_THUE': related.KH_THUE,
                    'MS_THUE': related.MS_THUE,
                    'DC_THUE': related.DC_THUE,
                    'BO_PHAN': related.BO_PHAN.id if related.BO_PHAN else False,
                    'VVIEC': related.VVIEC.id if related.VVIEC else False,
                    'KHO': related.KHO.id if related.KHO else False,
                    'KHOAN_MUC': related.KHOAN_MUC.id if related.KHOAN_MUC else False,
                    'TIEN_TE': related.TIEN_TE.id if related.TIEN_TE else False,
                    'TY_GIA': related.TY_GIA,
                    'MA_TK1_ID': related.MA_TK1_ID.id if related.MA_TK1_ID else False,
                    'DVCS': related.DVCS.id if related.DVCS else False,
                    'CHI_NHANH': related.CHI_NHANH.id if related.CHI_NHANH else False,
                    'MENU_ID': related.MENU_ID.id if related.MENU_ID else False,
                })

        # --- Tạo bản ghi acc.ap.d ---
        rec = super(AccApD, self).create(vals)

        # if '...' not in rec.GHI_CHU:

        # vals_dict = {
        #     "HANG_HOA": rec.HANG_HOA.id,
        #     "MA_TK0": rec.MA_TK0 or "",
        #     "SO_LUONG": rec.SO_LUONG,
        #     "DON_GIA": rec.DON_GIA,
        #     "PS_NO1": rec.PS_NO1,
        #     "TIEN_NTE": rec.TIEN_NTE,
        #     "VAT": rec.VAT,
        #     "NGAY_CT": str(rec.NGAY_CT),
        #     "CHUNG_TU": rec.CHUNG_TU or "",
        #     "CTGS": rec.CTGS or "",
        #     "SO_HD": rec.SO_HD or "",
        #     "SERI_HD": rec.SERI_HD or "",
        #     "NGAY_HD": str(rec.NGAY_HD) or "",
        #     "MAU_SO": rec.MAU_SO,
        #     "PT_THUE": rec.PT_THUE.PT_THUE,
        #     "ONG_BA": rec.ONG_BA,
        #     "GHI_CHU": rec.GHI_CHU,
        #     "KHACH_HANG": rec.KHACH_HANG.id,
        #     "KH_THUE": rec.KH_THUE,
        #     "MS_THUE": rec.MS_THUE,
        #     "DC_THUE": rec.DC_THUE,
        #     "BO_PHAN": rec.BO_PHAN.id,
        #     "VVIEC": rec.VVIEC.id,
        #     "KHO": rec.KHO.id,
        #     "KHOAN_MUC": rec.KHOAN_MUC.id,
        #     "TIEN_TE": rec.TIEN_TE.id,
        #     "TY_GIA": rec.TY_GIA,
        #     "MA_TK1": rec.MA_TK1,
        #     "DVCS": rec.DVCS.id or 1,
        #     "CHI_NHANH": rec.CHI_NHANH.id,
        #     "MENU_ID": rec.MENU_ID.id or 337,
        #     "BUT_TOAN_THEM": True
        # }
        # json_data = json.dumps(vals_dict)
        # self.env.cr.execute("SELECT * FROM fn_bt_them(%s::jsonb);", [json_data])
        # rows = self.env.cr.dictfetchall()
        #
        # for data in rows:
        #     mapped_vals = {}
        #     for key, value in data.items():
        #         upper_key = key.upper()
        #         if upper_key in self._fields:
        #             mapped_vals[upper_key] = value
        #     new_d = super(AccApD, self).create(mapped_vals)




        # --- Chuẩn bị dữ liệu để insert vào bảng tổng hợp ---
        raw = rec.read()[0]
        custom_fields = [f for f in self._fields.keys() if f.upper() == f and f not in ('ID',)]

        data = {}
        for fld in custom_fields:
            if fld in raw:
                val = raw[fld]
                if isinstance(val, (list, tuple)):  # M2O
                    data[fld] = val[0] if val else None
                else:
                    data[fld] = val

        # --- Thêm khóa ngoại ---
        data['ACC_AP_D'] = rec.id

        # --- Loại bỏ toàn bộ system fields (tránh lỗi CREATE_DATE, WRITE_UID, __last_update, …) ---
        system_fields = {'CREATE_UID', 'CREATE_DATE', 'WRITE_UID', 'WRITE_DATE', '__LAST_UPDATE'}
        clean_data = {k: v for k, v in data.items() if k not in system_fields}

        table_name = 'nl_acc_tong_hop'
        if not re.match(r'^[A-Za-z0-9_]+$', table_name):
            raise ValueError("Tên bảng không hợp lệ!")

        # --- Tạo cột nếu cần ---
        self.create_dynamic_fields(table_name, clean_data)

        # --- Build câu lệnh SQL ---
        cols = [f'"{k.upper()}"' for k in clean_data.keys()]
        placeholders = ', '.join(['%s'] * len(clean_data))
        values = list(clean_data.values())

        sql = f'INSERT INTO "{table_name}" ({", ".join(cols)}) VALUES ({placeholders});'
        self._cr.execute(sql, values)
        self._cr.commit()

        _logger.info(f"[AUTO] Inserted acc.ap.d id={rec.id} into {table_name}")

        return rec

