# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from erppeek import Client
from openerp.exceptions import Warning


class Contract(models.Model):
    _inherit = 'support.contract'
    _description = 'support.contract'

    @api.multi
    def create_issue(self, vals):
        self.ensure_one()
        client = self.get_connection()
        module = 'web_support_server_issue'
        if client.modules(name=module, installed=True) is None:
            raise Warning(_('You can not load an issue if suppor server do not\
                have "%s" module installed.') % module)
        # issue_id = client.model('account.analytic.account').create(vals)
        res = self.get_remote_contract().create_issue(
            self._cr.dbname, self.env.user.id, vals)
        print 'res', res
        # TODO implementar devolver la url de acceso al issue
        return res['issue_id']

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
