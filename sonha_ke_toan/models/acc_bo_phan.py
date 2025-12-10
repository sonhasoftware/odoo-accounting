from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError
import json


class AccBoPhan(models.Model):
    _name = 'acc.bo.phan'
    _order = 'MA,CAP,DVCS'
    _rec_name = 'MA_TEN'

    CAP = fields.Integer(string="Cấp", store=True)
    MA = fields.Char(string="Mã", store=True)
    TEN = fields.Char(string="Tên", store=True)
    MA_TEN = fields.Char(string="Mã - Tên", store=True, readonly=True, compute="get_ma_ten")
    BO_PHAN = fields.Integer(string="Bộ phận", store=True, compute="_get_bo_phan")
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)
    ACTIVE = fields.Boolean(string="ACTIVE", store=True)

    @api.depends('MA', 'TEN')
    def get_ma_ten(self):
        for r in self:
            r.MA_TEN = f"{r.MA} - {r.TEN}" if (r.MA and r.TEN) else ""

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, access_rights_uid=None):
        dvcs = self.env.company.id
        nguoi_dung = self.env.uid

        # Gọi function PostgreSQL
        query = "SELECT * FROM public.fn_acc_bo_phan(%s, %s)"
        self.env.cr.execute(query, (dvcs, nguoi_dung))
        rows = self.env.cr.dictfetchall()

        # Lấy danh sách id từ function
        ids = [row["id"] for row in rows if "id" in row]

        # Trả domain ép buộc Odoo chỉ lấy các bản ghi này
        new_domain = args + [("id", "in", ids)] if ids else [("id", "=", 0)]

        return super(AccBoPhan, self)._search(
            new_domain,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid,
        )

    @api.model
    def search_count(self, args):
        ids = self._search(args)
        return len(ids)

    def create(self, vals):
        # === SONPV: cập nhật MA_TEN sau khi ghi ===
        for rec in self:
            ma = rec.MA or ''
            ten = rec.TEN or ''
            ma_ten = f"{ma} - {ten}" if (ma or ten) else ''
            rec.MA_TEN = ma_ten
        # === END SONPV ===

        rec = super(AccBoPhan, self).create(vals)
        rec.BO_PHAN = rec.id
        dvcs = rec.DVCS.id

        vals_dict = {
            "CAP": rec.CAP or "",
            "MA": rec.MA or "",
            "TEN": rec.TEN or "",
            "MA_TEN": rec.MA_TEN or "",
            "BO_PHAN": rec.BO_PHAN or 0,
            "DVCS": rec.DVCS.id or 1,
            "NGUOI_TAO": self.env.uid or None,
            "NGUOI_SUA": self.env.uid or None,
        }

        json_data = json.dumps(vals_dict)
        self.env.cr.execute("SELECT * FROM fn_check_nl(%s::jsonb);", [json_data])
        check = self.env.cr.dictfetchall()
        if check:
            result = check[0]
            loi = list(result.values())[0]
            raise ValidationError(loi)

        self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_bo_phan', dvcs])

        return rec

    def write(self, vals):
        res = super(AccBoPhan, self).write(vals)

        # === SONPV: cập nhật MA_TEN sau khi ghi ===
        for rec in self:
            ma = rec.MA or ''
            ten = rec.TEN or ''
            ma_ten = f"{ma} - {ten}" if (ma or ten) else ''
            # Cập nhật trực tiếp không gọi lại write()
            self.env.cr.execute("""
                                UPDATE acc_bo_phan
                                SET "MA_TEN" = %s
                                WHERE id = %s
                                """, (ma_ten, rec.id))

            vals_dict = {
                "CAP": rec.CAP or "",
                "MA": rec.MA or "",
                "TEN": rec.TEN or "",
                "MA_TEN": rec.MA_TEN or "",
                "BO_PHAN": rec.BO_PHAN or 0,
                "DVCS": rec.DVCS.id or 1,
                "NGUOI_TAO": rec.create_uid.id or None,
                "NGUOI_SUA": self.env.uid or None,
            }

            json_data = json.dumps(vals_dict)
            table_name = 'acc.bo.phan'

            self.env.cr.execute("""
                SELECT * FROM fn_check_nl(%s::text, %s::jsonb);
            """, (table_name, json_data))
            check = self.env.cr.dictfetchall()
            if check:
                result = check[0]
                loi = list(result.values())[0]
                if loi == None:
                    pass
                else:
                    raise ValidationError(loi)
        # === END SONPV ===

        dvcs = self.DVCS.id
        self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_bo_phan', dvcs])

        return res

    def unlink(self):
        res = super(AccBoPhan, self).unlink()
        dvcs = self.DVCS.id
        self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_bo_phan', dvcs])
        return res

    @api.constrains('MA')
    def _check_unique_ma(self):
        for rec in self:
            if rec.MA:
                exists = self.search([
                    ('MA', '=', rec.MA),
                    ('id', '!=', rec.id)
                ], limit=1)
                if exists:
                    raise ValidationError("Mã %s đã tồn tại, vui lòng nhập mã khác!" % rec.MA)

    # def check_access_rights(self, operation, raise_exception=True):
    #     # gọi super để giữ nguyên quyền mặc định nếu cần
    #     res = super().check_access_rights(operation, raise_exception=False)
    #
    #     # lấy đơn vị của bản ghi (nếu có field company_id / dv / đơn vị)
    #     company_id = self.env.company.id  # mặc định là công ty hiện tại của user
    #
    #     # tìm quyền phân bổ cho user hiện tại và đúng đơn vị
    #     access = self.env['sonha.phan.quyen'].sudo().search([
    #         ('NGUOI_DUNG', '=', self.env.uid),
    #         ('TEN_BANG', '=', self._name),
    #         ('DVCS', '=', company_id),
    #     ], limit=1)
    #
    #     allowed = False
    #     if access:
    #         if operation == 'read' and access.XEM_DM:
    #             allowed = True
    #         elif operation == 'create' and access.THEM_DM:
    #             allowed = True
    #         elif operation == 'write' and access.SUA_DM:
    #             allowed = True
    #         elif operation == 'unlink' and access.XOA_DM:
    #             allowed = True
    #     else:
    #         allowed = False
    #
    #     if not allowed:
    #         if raise_exception:
    #             raise exceptions.AccessError(
    #                 _("Bạn không có quyền %s trên %s (Đơn vị: %s)") %
    #                 (operation, self._description, self.env.company.name)
    #             )
    #         return False
    #
    #     return True

