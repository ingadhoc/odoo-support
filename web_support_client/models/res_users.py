# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, SUPERUSER_ID, exceptions, _
from ast import literal_eval
from openerp.addons.server_mode.mode import get_mode
from openerp.exceptions import ValidationError
import logging
import urlparse
import urllib
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    remote_partner_uuid = fields.Char(
        'Remote Partner UUID',
        readonly=False,
        copy=False,
    )

    @api.multi
    def action_reset_password(self):
        self.check_pass_change()
        return super(ResUsers, self).action_reset_password()

    @api.multi
    @api.constrains('password', 'login', 'groups_id')
    def check_pass_change(self):
        for rec in self:
            if rec.id == SUPERUSER_ID and rec.env.user.id != SUPERUSER_ID:
                raise ValidationError(_(
                    'Only Admin can change his password, login and groups'))

    @api.model
    def check_credentials(self, password):
        """
        Si el usuario es admin permitimos login con pass de instancia tmb
        Si el usuario es otro, permitimos con pass intancia o admin solo si:
        * no produccion
        * producción y allow on production True
        """
        passkey_allowed = True
        if not get_mode():
            if not literal_eval(
                    self.env['ir.config_parameter'].sudo().get_param(
                        'auth_admin_passkey.allow_on_production',
                        'True')):
                passkey_allowed = False
        if self.env.uid != SUPERUSER_ID and passkey_allowed:
            # try with user pass
            try:
                super(ResUsers, self).check_credentials(password)
                return True
            except exceptions.AccessDenied:
                # try with instance password
                try:
                    self.check_super(password)
                    return True
                except exceptions.AccessDenied:
                    # try with admin password
                    return self.sudo().check_credentials(password)
        # si es super admin, probamos tmb con clave de instancia
        elif self.env.uid == SUPERUSER_ID:
            # try with instance password
            try:
                self.check_super(password)
            except exceptions.AccessDenied:
                return super(ResUsers, self).check_credentials(password)
        # si no es super admin y no hay passkey allowed, entonces por defecto
        else:
            return super(ResUsers, self).check_credentials(password)

    @api.model
    def get_signup_url(self):
        remote_partner_uuid = self.browse(self._uid).remote_partner_uuid
        active_contract = self.env['support.contract'].get_active_contract(
            do_not_raise=True)
        url = active_contract.server_host
        if remote_partner_uuid and url:
            params = {
                'partner_uuid': remote_partner_uuid,
            }
            url = urlparse.urljoin(url, 'partner_uuid/signin')
            url += '?' + urllib.urlencode(params)
        return url
