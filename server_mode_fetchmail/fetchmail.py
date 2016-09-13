# -*- coding: utf-8 -*-
import logging
from openerp import models, api, _
from openerp.exceptions import UserError
from openerp.addons.server_mode.mode import get_mode

_logger = logging.getLogger(__name__)


class fetchmail_server(models.Model):
    _inherit = 'fetchmail.server'

    @api.multi
    def button_confirm_login(self):
        if get_mode():
            raise UserError(_(
                "You Can not Confirm & Test Because Odoo is in %s mode.") % (
                get_mode()))
        return super(fetchmail_server, self).button_confirm_login()

    @api.multi
    def fetch_mail(self):
        if get_mode():
            raise UserError(_(
                "You Can not Fetch Mail Because Odoo is in %s mode.") % (
                get_mode()))
        return super(fetchmail_server, self).fetch_mail()

    @api.cr_uid_ids_context
    def connect(self, cr, uid, server_id, context=None):
        if isinstance(server_id, (list, tuple)):
            server_id = server_id[0]
        if get_mode():
            raise UserError(_(
                "Can not Connect to server because Odoo is in %s mode.") % (
                get_mode()))
        return super(fetchmail_server, self).connect(
            cr, uid, server_id=server_id, context=context)
