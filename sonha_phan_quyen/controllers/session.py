from odoo import http
from odoo.http import request


class SonhaSessionController(http.Controller):

    @http.route('/sonha/session/is_alive', type='json', auth='public', csrf=False)
    def is_alive(self):
        uid = request.session.uid
        if not uid:
            return {'is_alive': False}

        env = request.env(user=uid)
        user = env['res.users'].sudo().browse(uid)
        login_locked = env['ir.config_parameter'].sudo().get_param(
            user.SONHA_LOGIN_LOCK_PARAM
        ) == '1'

        if login_locked and user.exists() and not user.has_group('base.group_system'):
            request.session.logout(keep_db=True)
            return {'is_alive': False}

        return {'is_alive': True}
