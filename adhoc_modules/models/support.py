# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'support.contract'

    @api.model
    def _cron_update_adhoc_modules(self):
        contract = self.get_active_contract()
        try:
            contract.get_adhoc_modules_data()
        except:
            _logger.error(
                "Error Updating ADHOC Modules Data For Contract %s" % (
                    contract.name))

    @api.multi
    def get_adhoc_modules_data(self):
        # we send contract_id so it can be used in other functions
        self = self.with_context(
            contract_id=self.contract_id)
        self.ensure_one()
        _logger.info(
            "Updating Updating ADHOC Modules Data For Contract %s" % self.name)
        adhoc_server_module = 'adhoc_modules_server'
        if not self.check_modules_installed([adhoc_server_module]):
            raise Warning((
                'Can not sync modules data because module "%s" is not '
                'installed on support provider database'))
        client = self.get_connection()
        self.update_adhoc_categories(client)
        self.update_adhoc_modules(client)

    @api.model
    def update_adhoc_categories(self, client):
        contract_id = self._context.get('contract_id')
        fields = [
            'name',
            'code',
            'parent_id',
            'visibility',
            'description',
            'sequence',
        ]
        updated_records = local_model = self.env['adhoc.module.category']
        remote_model = client.model('adhoc.module.category.server')

        remote_datas = remote_model.search_read(
            [], fields, 0, None, 'parent_left')
        for remote_data in remote_datas:
            # we dont wont or need id
            category_id = remote_data.pop('id')
            parent_data = remote_data.pop('parent_id')
            if parent_data:
                parent_code = remote_model.search_read(
                    [('id', '=', parent_data[0])], ['code'])[0]['code']
                parent = local_model.search([
                    ('code', '=', parent_code)], limit=1)
                remote_data['parent_id'] = parent.id
            local_record = local_model.search([
                ('code', '=', remote_data.get('code'))], limit=1)
            if remote_data['visibility'] == 'product_required':
                remote_data['contracted_product'] = (
                    remote_model.get_related_contracted_product(
                        category_id, contract_id))
            if local_record:
                local_record.write(remote_data)
            else:
                local_record = local_record.create(remote_data)
            updated_records += local_record
        # remove records that has not been updated (they dont exist anymore)
        (local_model.search([]) - updated_records).unlink()

    @api.model
    def update_adhoc_modules(self, client):
        fields = [
            'name',
            'adhoc_category_id',
            'adhoc_summary',
            'adhoc_description_html',
            'support_type',
            'review',
            'conf_visibility',
            'visibility_obs',
        ]
        local_model = self.env['ir.module.module']
        remote_model = client.model('adhoc.module.module')

        remote_datas = remote_model.search_read(
            [], fields)
        for remote_data in remote_datas:
            # we dont wont or need id
            remote_data.pop('id')
            category_data = remote_data.pop('adhoc_category_id')
            if category_data:
                category_code = client.model(
                    'adhoc.module.category.server').search_read(
                        [('id', '=', category_data[0])], ['code'])[0]['code']
                adhoc_category = self.env['adhoc.module.category'].search([
                    ('code', '=', category_code)], limit=1)
                remote_data['adhoc_category_id'] = (
                    adhoc_category and adhoc_category.id or False)
            local_record = local_model.search([
                ('name', '=', remote_data.get('name'))], limit=1)
            if local_record:
                local_record.write(remote_data)
            else:
                _logger.warning(
                    'Module %s not found on database, you can try updating db'
                    ' list' % remote_data.get('name'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
