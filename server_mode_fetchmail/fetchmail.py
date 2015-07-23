# -*- coding: utf-8 -*-
##############################################################################
#
#    BizzAppDev
#    Copyright (C) 2015-TODAY
#    bizzappdev(<http://www.bizzappdev.com>).
#    ADHOC SA(<http://www.adhoc.com.ar>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from openerp import models, api, _
from openerp.exceptions import Warning
from openerp.addons.server_mode.mode import get_mode

_logger = logging.getLogger(__name__)


class fetchmail_server(models.Model):
    _inherit = 'fetchmail.server'

    @api.multi
    def button_confirm_login(self):
        if get_mode():
            raise Warning(_(
                "You Can not Confirm & Test Because Odoo is in %s mode.") % (
                get_mode()))
        return super(fetchmail_server, self).button_confirm_login()

    @api.multi
    def fetch_mail(self):
        if get_mode():
            raise Warning(_(
                "You Can not Fetch Mail Because Odoo is in %s mode.") % (
                get_mode()))
        return super(fetchmail_server, self).fetch_mail()

    @api.cr_uid_ids_context
    def connect(self, cr, uid, server_id, context=None):
        if isinstance(server_id, (list, tuple)):
            server_id = server_id[0]
        if get_mode():
            raise Warning(_(
                "Can not Connect to server because Odoo is in %s mode.") % (
                get_mode()))
        return super(fetchmail_server, self).connect(
            cr, uid, server_id=server_id, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
