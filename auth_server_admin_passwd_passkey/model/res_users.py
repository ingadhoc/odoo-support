# -*- encoding: utf-8 -*-
from openerp import models, exceptions
from openerp import SUPERUSER_ID, api


class res_users(models.Model):
    _inherit = "res.users"

    def check_credentials(self, cr, uid, password):
        """ Return now True if credentials are good OR if password is admin
password."""
        # try default password
        try:
            super(res_users, self).check_credentials(
                cr, uid, password)
            return True
        except exceptions.AccessDenied:
            # try with instance pass
            try:
                self.check_super(password)
                return True
            except exceptions.AccessDenied:
                # try with admin user pass
                if uid != SUPERUSER_ID:
                    try:
                        super(res_users, self).check_credentials(
                            cr, uid, password)
                        return True
                    except exceptions.AccessDenied:
                        return self.check_credentials(
                            cr, SUPERUSER_ID, password)
                else:
                    return super(res_users, self).check_credentials(
                        cr, uid, password)

    @api.model
    def _send_email_passkey(self, user_agent_env):
        # disable send mail functionality
        return True

    @api.cr
    def _send_email_same_password(self, login_user):
        # disable send mail functionality
        return True
