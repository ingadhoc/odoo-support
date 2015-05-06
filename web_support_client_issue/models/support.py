# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'support.contract'
    _description = 'support.contract'

    @api.multi
    def create_issue(self, vals, attachments):
        self.ensure_one()
        client = self.get_connection()
        module = 'web_support_server_issue'
        if client.modules(name=module, installed=True) is None:
            raise Warning(_('You can not load an issue if suppor server do not\
                have "%s" module installed.') % module)
        _logger.info('Creating issue for db %s, with user %s and vals %s' % (
            self._cr.dbname, self.env.user.id, vals))

        attachments_data = attachments.read(['name', 'datas'])

        res = self.get_remote_contract().create_issue(
            self._cr.dbname, self.env.user.id, vals, attachments_data)
        if res.get('error'):
            raise Warning(_('Could not create issue, this is what we get:\n\
                %s') % res.get('error'))
        elif not res.get('issue_id'):
            raise Warning(_('Could not create issue, please contact your\
                support provider'))
        # TODO implementar devolver la url de acceso al issue
        return res['issue_id']

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
