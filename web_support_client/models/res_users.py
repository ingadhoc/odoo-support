# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, SUPERUSER_ID, exceptions
from ast import literal_eval
from openerp.addons.server_mode.mode import get_mode
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    remote_partner_uuid = fields.Char(
        'Remote Partner UUID',
        readonly=False,
        copy=False,
    )

    @api.model
    def check_credentials(self, password):
        """ Return now True if credentials are good OR if password is admin
password."""
        passkey_allowed = True
        if not get_mode():
            if not literal_eval(
                    self.env['ir.config_parameter'].sudo().get_param(
                        'auth_admin_passkey.allow_on_production',
                        'True')):
                passkey_allowed = False
        if self.env.uid != SUPERUSER_ID and passkey_allowed:
            try:
                super(ResUsers, self).check_credentials(password)
                return True
            except exceptions.AccessDenied:
                return self.sudo().check_credentials(password)
        else:
            return super(ResUsers, self).check_credentials(password)
