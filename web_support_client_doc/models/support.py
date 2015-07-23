# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'support.contract'

    @api.model
    def _cron_update_website_doc(self):
        contracts = self.search([])
        for contract in contracts:
            try:
                contract.get_documentation_data()
            except:
                _logger.error(
                    "Error Updating Documentation Data For Contract %s" % (
                        contract.name))

    @api.one
    def get_documentation_data(self):
        _logger.info("Updating Documentation Data For Contract %s" % self.name)
        client = self.get_connection()
        installed_modules = self.env['ir.module.module'].search(
            [('state', '=', 'installed')])
        installed_module_names = [x.name for x in installed_modules]
        # TODO hay que mejorar y ver que si no puedo leer un padre tampoco
        # puedo leer un hijo
        doc_ids = client.model('website.doc.toc').search([
            '|', ('required_module_id.name', 'in', installed_module_names),
            ('required_module_id', '=', False)])
        imp_fields = [
            'id',
            'name',
            'parent_id/id',
            'is_article',
            'add_google_doc',
            'google_doc_link',
            'google_doc_code',
            'google_doc_height',
            'content',
            ]
        # export and load data
        doc_data = client.model('website.doc.toc').export_data(
            doc_ids, imp_fields)['datas']
        doc_toc = self.env['website.doc.toc']
        doc_toc.load(imp_fields, doc_data)

        # clean remove data
        doc_toc_data = doc_toc.search([]).export_data(['id'])['datas']
        actual_refs = [x[0] for x in doc_toc_data if x[0]]
        imported_refs = [x[0] for x in doc_data]
        to_remove_refs = list(set(actual_refs) - set(imported_refs))
        for record_ref in to_remove_refs:
            record = self.env.ref(record_ref)
            record.unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
