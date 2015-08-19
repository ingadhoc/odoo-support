# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.addons.web import http
from openerp.addons.server_mode import mode as custom_mode
openerpweb = http


class mode(openerpweb.Controller):
    _cp_path = "/web/mode"

    @openerpweb.jsonrequest
    def get_mode(self, req, mode=False, db=False):
        if mode != custom_mode.get_mode():
            return False
        return custom_mode.get_mode()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
