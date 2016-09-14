# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.addons.server_mode import mode as custom_mode
from openerp.addons.web.controllers.main import Home
import openerp.tools as tools
from openerp.http import request
from openerp import http
openerpweb = http


class mode(openerpweb.Controller):
    _cp_path = "/web/mode"

    @openerpweb.jsonrequest
    def get_mode(self, req, db=False):
        if custom_mode.get_mode():
            return custom_mode.get_mode().upper()
        return False


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
#
class Mode_Server(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        modet = tools.config.get('server_mode')
        if modet:
            request.params['mode'] = modet.upper()

        return super(Mode_Server, self).web_login(**kw)
