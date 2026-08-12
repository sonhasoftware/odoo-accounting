from odoo import http
from odoo.http import request


class SonhaSessionController(http.Controller):

    @http.route('/sonha/session/is_alive', type='json', auth='public', csrf=False)
    def is_alive(self):
        return {'is_alive': bool(request.session.uid)}
