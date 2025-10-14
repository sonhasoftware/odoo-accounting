from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccBom(models.Model):
    _name = 'acc.bom'

    SAN_PHAM = fields.Many2one('acc.san.pham', string="Mã SP", store=True, readonly=True)
    SAN_PHAM_NAME = fields.Char(related='SAN_PHAM.TEN', string="Tên SP", store=True, readonly=True)

    HANG_HOA = fields.Many2one('acc.hang.hoa', string="Mã hàng", store=True)
    HANG_HOA_NAME = fields.Char(related='HANG_HOA.TEN', string="Tên hàng", store=True)

    SO_LUONG = fields.Float(string="Định mức(SL)", store=True)
    SLDM = fields.Float(string="ĐM trên SL", store=True)
    LOAI_DM = fields.Selection([('bo', "Bộ"),
                                ('sp', "SP"),
                                ('khac', "Khác")],
                               string="Loại DM", store=True)
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
    #     return super(AccDongHang, self)._search(
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