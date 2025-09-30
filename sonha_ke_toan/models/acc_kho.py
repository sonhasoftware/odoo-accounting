from odoo import api, fields, models, exceptions, _


class AccKho(models.Model):
    _name = 'acc.kho'

    CAP = fields.Boolean(string="Cấp", store=True)
    MA = fields.Char(string="Mã", store=True)
    TEN = fields.Char(string="Tên", store=True)
    KHO = fields.Integer(string="Kho", store=True)
    DVCS = fields.Integer(string="ĐV", store=True)
    ACTIVE = fields.Boolean(string="ACTIVE", store=True)

    def check_access_rights(self, operation, raise_exception=True):
        # gọi super để giữ nguyên quyền mặc định nếu cần
        res = super().check_access_rights(operation, raise_exception=False)

        # tìm quyền phân bổ cho user hiện tại
        access = self.env['sonha.phan.quyen'].sudo().search([
            ('NGUOI_DUNG.user_id', '=', self.env.uid),
            ('TEN_BANG', '=', self._name)
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
                    _("Bạn không có quyền %s trên %s") % (operation, self._description)
                )
            return False

        return True
