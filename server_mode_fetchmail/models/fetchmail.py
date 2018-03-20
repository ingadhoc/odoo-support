from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.addons.server_mode.mode import get_mode


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    @api.multi
    def button_confirm_login(self):
        if get_mode():
            raise UserError(_(
                "You Can not Confirm & Test Because Odoo is in %s mode.") % (
                get_mode()))
        return super(FetchmailServer, self).button_confirm_login()

    @api.multi
    def fetch_mail(self):
        if get_mode():
            raise UserError(_(
                "You Can not Fetch Mail Because Odoo is in %s mode.") % (
                get_mode()))
        return super(FetchmailServer, self).fetch_mail()

    @api.multi
    def connect(self):
        if get_mode():
            raise UserError(_(
                "Can not Connect to server because Odoo is in %s mode.") % (
                get_mode()))
        return super(FetchmailServer, self).connect()
