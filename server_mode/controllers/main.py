##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.server_mode import mode as custom_mode
from odoo.addons.web.controllers.main import Home
import odoo.tools as tools
from odoo.http import request
from odoo import http


class mode(http.Controller):

    @http.route('/web/mode', type='json', auth='none')
    def get_mode(self, req, db=False):
        if custom_mode.get_mode():
            return custom_mode.get_mode().upper()
        return False


class Mode_Server(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        mode = tools.config.get('server_mode')
        if mode:
            request.params['mode'] = mode.upper()

        return super(Mode_Server, self).web_login(**kw)
