# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'support.contract'
    _description = 'support.contract'

    @api.multi
    def create_issue(self, vals, attachments):
        _logger.info('Creating issue for db %s, with user %s and vals %s' % (
            self._cr.dbname, self.env.user.login, vals))

        self.ensure_one()
        client = self.get_connection()
        module = 'web_support_server_issue'
        _logger.info('Checking module %s exist on support provider' % module)
        if client.modules(name=module, installed=True) is None:
            raise Warning(_(
                'You can not load an issue if suppor server do not have\
                "%s" module installed. Pleas contact support provider'
                ) % module)

        _logger.info('Reading attachments data')
        attachments_data = attachments.read(['name', 'datas'])

        _logger.info('Creating issue')
        res = client.model('account.analytic.account').create_issue(
            self.contract_id,
            self._cr.dbname,
            self.env.user.login,
            vals,
            attachments_data)

        if res.get('error'):
            raise Warning(_('Could not create issue, this is what we get:\n\
                %s') % res.get('error'))
        elif not res.get('issue_id'):
            raise Warning(_('Could not create issue, please contact your\
                support provider'))
        return res['issue_id']

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
