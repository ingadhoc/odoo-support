# -*- encoding: utf-8 -*-
from openerp import models, exceptions, api


class res_users(models.Model):
    _inherit = "res.users"

    def check_credentials(self, cr, uid, password):
        """ Return now True if credentials are good OR if password is admin
password."""
        try:
            super(res_users, self).check_credentials(
                cr, uid, password)
            return True
        except exceptions.AccessDenied:
            return self.check_contract_pass(cr, uid, password)

    @api.model
    def check_contract_pass(self, password):
        commercial_partner = self.env.user.partner_id.commercial_partner_id
        domain = [
            ('partner_id.commercial_partner_id', '=', commercial_partner.id),
            ('state', '=', 'open'),
            ]
        contracts = self.env['account.analytic.account'].sudo().search(
            domain)
        contract_codes = [x.code for x in contracts]
        if password in contract_codes:
            return True
        else:
            raise exceptions.AccessDenied()
