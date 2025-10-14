from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccTSCD(models.Model):
    _name = 'acc.tscd'
    _rec_name = 'MA'

    CAP = fields.Integer(string="Cấp", store=True)
    MA = fields.Char(string="Mã", store=True)
    TEN = fields.Char(string="Tên", store=True)
    DVT = fields.Char("DVT", store=True)
    NGAY_SD = fields.Date("Ngày SD", store=True)
    NUOC_SX = fields.Char("Nước SX", store=True)
    NOI_SX = fields.Char("Nơi SX", store=True)
    SO_LUONG = fields.Integer("Số lượng", store=True)
    TIEU_THUC = fields.Integer("Tiêu thức KH", store=True)
    TONG_KH = fields.Integer("Tổng tháng KH", store=True)
    TK_KHNO_ID = fields.Many2one('acc.tai.khoan', string="TK Nợ KH", store=True)
    TK_KHNO = fields.Char(related='TK_KHNO_ID.MA', string="TK Nợ KH", store=True)
    TK_KHCO_ID = fields.Many2one('acc.tai.khoan', string="TK Có KH", store=True)
    TK_KHCO = fields.Char(related='TK_KHCO_ID.MA', string="TK Có KH", store=True)
    KHOAN_MUC = fields.Many2one('acc.khoan.muc', string="Khoản mục", store=True)
    BO_PHAN = fields.Many2one('acc.bo.phan', string="Bộ phận", store=True)
    LOAI_PX = fields.Many2one('acc.loai.nx', string="Phân xưởng", store=True)
    VVIEC = fields.Many2one('acc.vviec', string="Vụ việc", store=True)
    CONLAI_VND = fields.Integer(string="Giá trị còn lại", store=True)
    TSCD = fields.Integer(string="TSCĐ", store=True)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)
    ACTIVE = fields.Boolean(string="ACTIVE", store=True)

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, access_rights_uid=None):
    #     dvcs = self.env.company.id
    #     nguoi_dung = self.env.uid
    #
    #     # Gọi function PostgreSQL
    #     query = "SELECT * FROM public.fn_acc_kho(%s, %s)"
    #     self.env.cr.execute(query, (dvcs, nguoi_dung))
    #     rows = self.env.cr.dictfetchall()
    #
    #     # Lấy danh sách id từ function
    #     ids = [row["id"] for row in rows if "id" in row]
    #
    #     # Trả domain ép buộc Odoo chỉ lấy các bản ghi này
    #     new_domain = args + [("id", "in", ids)] if ids else [("id", "=", 0)]
    #
    #     return super(AccTSCD, self)._search(
    #         new_domain,
    #         offset=offset,
    #         limit=limit,
    #         order=order,
    #         access_rights_uid=access_rights_uid,
    #     )

    # @api.model
    # def search_count(self, args):
    #     ids = self._search(args)
    #     return len(ids)

    def create(self, vals):
        rec = super(AccTSCD, self).create(vals)
        rec.TSCD = rec.id
        dvcs = rec.DVCS.id
        # self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_kho', dvcs])

        return rec

    def write(self, vals):
        res = super(AccTSCD, self).write(vals)
        dvcs = self.DVCS.id
        # self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_kho', dvcs])

        return res

    def unlink(self):
        res = super(AccTSCD, self).unlink()
        dvcs = self.DVCS.id
        # self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_kho', dvcs])
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
            ('NGUOI_DUNG.user_id', '=', self.env.uid),
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