from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccLoaiDL(models.Model):
    _name = 'acc.loaidl'
    _rec_name = 'MA'

    CAP = fields.Integer(string="Cấp", store=True)
    MA = fields.Char(string="Mã", store=True)
    TEN = fields.Char(string="Tên", store=True)
    LOAIDL = fields.Integer(string="Loại DL", store=True)
    STT = fields.Integer(string="STT", store=True)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)
    ACTIVE = fields.Boolean(string="ACTIVE", store=True)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, access_rights_uid=None):
        dvcs = self.env.company.id
        nguoi_dung = self.env.uid

        # Gọi function PostgreSQL
        query = "SELECT * FROM public.fn_acc_loaidl(%s, %s)"
        self.env.cr.execute(query, (dvcs, nguoi_dung))
        rows = self.env.cr.dictfetchall()

        # Lấy danh sách id từ function
        ids = [row["id"] for row in rows if "id" in row]

        # Trả domain ép buộc Odoo chỉ lấy các bản ghi này
        new_domain = args + [("id", "in", ids)] if ids else [("id", "=", 0)]

        return super(AccLoaiDL, self)._search(
            new_domain,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid,
        )

    def create(self, vals):
        rec = super(AccLoaiDL, self).create(vals)
        dvcs = rec.DVCS.id
        self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_loaidl', dvcs])

        return rec

    def write(self, vals):
        res = super(AccLoaiDL, self).write(vals)
        dvcs = self.DVCS.id
        self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_loaidl', dvcs])

        return res

    def unlink(self):
        res = super(AccLoaiDL, self).unlink()
        dvcs = self.DVCS.id
        self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_loaidl', dvcs])
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

    def check_access_rights(self, operation, raise_exception=True):
        # gọi super để giữ nguyên quyền mặc định nếu cần
        res = super().check_access_rights(operation, raise_exception=False)

        # lấy đơn vị của bản ghi (nếu có field company_id / dv / đơn vị)
        company_id = self.env.company.id  # mặc định là công ty hiện tại của user

        # tìm quyền phân bổ cho user hiện tại và đúng đơn vị
        access = self.env['sonha.phan.quyen'].sudo().search([
            ('NGUOI_DUNG', '=', self.env.uid),
            ('TEN_BANG', '=', self._name),
            ('DVCS', '=', company_id),
        ], limit=1)

        allowed = False
        if access:
            if operation == 'read' and access.XEM_DM:
                allowed = True
            elif operation == 'create' and access.THEM_DM:
                allowed = True
            elif operation == 'write' and access.SUA_DM:
                allowed = True
            elif operation == 'unlink' and access.XOA_DM:
                allowed = True
        else:
            allowed = False

        if not allowed:
            if raise_exception:
                raise exceptions.AccessError(
                    _("Bạn không có quyền %s trên %s (Đơn vị: %s)") %
                    (operation, self._description, self.env.company.name)
                )
            return False

        return True