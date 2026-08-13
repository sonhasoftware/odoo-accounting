from odoo import api, fields, models, registry
from odoo.exceptions import AccessDenied
from odoo.http import root, request


class SonhaUser(models.Model):
    _name = 'sonha.user'
    _rec_name = 'NAME'

    SONHA_USER = fields.Integer(string="User id", store=True)
    NAME = fields.Char(string="Tên", store=True)
    NGUOI_DUNG = fields.Many2one("res.users", string="Người dùng", store=True)
    NGAY_KHOA = fields.Date(string="Ngày khóa", store=True)
    SO_NGAY_KHOA = fields.Integer(string="Số ngày khóa", store=True)
    USER_KHAI_THAC = fields.Boolean(string="User khai thác", store=True)

    QUYEN_DOC = fields.Many2many('sonha.user', 'doc_dl_rel', 'doc_dl_phan_quyen', 'doc_dl_id',
                              string="Quyền đọc", store=True)
    QUYEN_SUA = fields.Many2many('sonha.user', 'write_dl_rel', 'write_dl_phan_quyen', 'write_dl_id',
                              string="Quyền sửa", store=True)

    def action_phan_quyen(self):
        for r in self:
            list_model = self.env['ir.model'].sudo().search([])
            list_model = list_model.filtered(lambda x: x.modules == 'sonha_ke_toan')
            for model in list_model:
                list_company = self.env.company
                for company in list_company:
                    check = self.env['sonha.phan.quyen'].sudo().search([('TEN_BANG', '=', model.id),
                                                                        ('NGUOI_DUNG_ID', '=', r.id),
                                                                        ('DVCS', '=', company.id),])

                    if not check:
                        self.env['sonha.phan.quyen'].sudo().create({
                            'NGUOI_DUNG_ID': r.id,
                            'TEN_BANG': model.id,
                            'DVCS': company.id,
                            'NGUOI_DUNG': r.NGUOI_DUNG.id or 0,
                            'SONHA_USER': r.id or 0,
                        })


    def create(self, vals):
        if 'QUYEN_SUA' in vals:
            vals = self._sync_quyen_doc(vals)
        rec = super(SonhaUser, self).create(vals)
        rec.SONHA_USER = rec.id
        return rec

    def write(self, vals):
        if 'QUYEN_SUA' in vals:
            vals = self._sync_quyen_doc(vals)
        return super(SonhaUser, self).write(vals)

    def _sync_quyen_doc(self, vals):
        """
        Add thêm user từ QUYEN_SUA sang QUYEN_DOC
        KHÔNG xoá quyền đọc cũ
        """

        if not vals.get('QUYEN_SUA'):
            return vals

        # Lấy user id được add vào QUYEN_SUA
        write_user_ids = set()

        for cmd in vals['QUYEN_SUA']:
            if cmd[0] == 6:  # replace
                write_user_ids.update(cmd[2])
            elif cmd[0] == 4:  # add
                write_user_ids.add(cmd[1])

        if not write_user_ids:
            return vals

        # Add thêm vào QUYEN_DOC
        doc_cmds = vals.get('QUYEN_DOC', [])
        for uid in write_user_ids:
            doc_cmds.append((4, uid))

        vals['QUYEN_DOC'] = doc_cmds
        return vals


class ResUsers(models.Model):

    _inherit = "res.users"

    SONHA_LOGIN_LOCK_PARAM = 'sonha_phan_quyen.login_locked'

    @api.model
    def _sonha_is_login_locked(self):
        return self.env['ir.config_parameter'].sudo().get_param(self.SONHA_LOGIN_LOCK_PARAM) == '1'

    @api.model
    def _sonha_set_login_lock(self, locked):
        self.env['ir.config_parameter'].sudo().set_param(
            self.SONHA_LOGIN_LOCK_PARAM,
            '1' if locked else '0',
        )

    @api.model
    def _sonha_logout_non_admin_sessions(self):
        current_sid = getattr(request.session, 'sid', False) if request else False
        session_store = root.session_store
        logged_out_count = 0

        for sid in session_store.list():
            if sid == current_sid:
                continue

            session = session_store.get(sid)
            session_uid = session.get('uid')
            if not session_uid:
                continue

            session_user = self.sudo().browse(session_uid)
            if session_user.exists() and not session_user.has_group('base.group_system'):
                session_store.delete(session)
                logged_out_count += 1

        return logged_out_count

    @classmethod
    def _login(cls, db, *args, **kwargs):
        uid = super()._login(db, *args, **kwargs)

        with registry(db).cursor() as cr:
            env = api.Environment(cr, uid, {})
            user = env['res.users'].sudo().browse(uid)
            login_locked = env['ir.config_parameter'].sudo().get_param(cls.SONHA_LOGIN_LOCK_PARAM) == '1'
            if login_locked and user.exists() and not user.has_group('base.group_system'):
                raise AccessDenied()

        return uid

    @api.model
    def action_lock_user_logins(self):
        if not self.env.user.has_group('base.group_system'):
            raise AccessDenied()

        self._sonha_set_login_lock(True)
        logged_out_count = self._sonha_logout_non_admin_sessions()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Lock đăng nhập',
                'message': 'Đã khóa đăng nhập và đăng xuất %s phiên của user không phải admin.' % logged_out_count,
                'type': 'success',
                'sticky': False,
            },
        }

    @api.model
    def action_unlock_user_logins(self):
        if not self.env.user.has_group('base.group_system'):
            raise AccessDenied()

        self._sonha_set_login_lock(False)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Unlock đăng nhập',
                'message': 'Đã mở khóa đăng nhập. User có thể đăng nhập lại bình thường.',
                'type': 'success',
                'sticky': False,
            },
        }

    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        self.env['sonha.user'].sudo().create({
            "NAME": user.name,
            "NGUOI_DUNG": user.id
        })

        return user
