# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
# from openerp import pooler
from openerp.exceptions import Warning
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta


class database_tools_configuration(models.TransientModel):
    _name = 'db.configuration'
    _inherit = 'res.config.settings'

    @api.model
    def _get_update_state(self):
        return self.env['ir.module.module'].get_overall_update_state()['state']

    @api.model
    def _get_update_detail(self):
        return self.env[
            'ir.module.module'].get_overall_update_state()['detail']

    @api.model
    def _get_backups_state(self):
        return self.env['db.database'].get_overall_backups_state()['state']

    @api.model
    def _get_backups_detail(self):
        return self.env['db.database'].get_overall_backups_state()['detail']

    backups_state = fields.Selection([
        ('ok', 'Ok'),
        ('error', 'Error'),
        ],
        string='Backups Status',
        readonly=True,
        default=_get_backups_state,
        )
    backups_detail = fields.Text(
        'Backups Status Detail',
        readonly=True,
        default=_get_backups_detail,
        )
    update_detail = fields.Text(
        'Update Detail',
        readonly=True,
        default=_get_update_detail,
        )
    update_state = fields.Selection([
        ('init_and_conf_required', 'Init and Config Required'),
        ('update_required', 'Update Required'),
        ('optional_update', 'Optional Update'),
        ('on_to_install', 'On To Install'),
        ('on_to_remove', 'On To Remove'),
        ('on_to_upgrade', 'On To Upgrade'),
        ('unmet_deps', 'Unmet Dependencies'),
        ('not_installable', 'Not Installable Modules'),
        ('ok', 'Ok'),
        ],
        'Update Status',
        readonly=True,
        default=_get_update_state,
        )

    # TODO if we want interaction with database_cleanup and purge everything
    # @api.model
    # def _get_purge_status_state(self):
    #     return self._get_purge_status()['state']

    # @api.model
    # def _get_purge_status_detail(self):
    #     return self._get_purge_status()['detail']

    # @api.model
    # def _get_purge_status(self):
    #     module_wizard = self.env['cleanup.purge.wizard.module'].create({})
    #     column_wizard = self.env['cleanup.purge.wizard.column'].create({})
    #     # data_wizard = self.env['cleanup.purge.wizard.data'].create({})
    #     menu_wizard = self.env['cleanup.purge.wizard.menu'].create({})
    #     model_wizard = self.env['cleanup.purge.wizard.model'].create({})
    #     table_wizard = self.env['cleanup.purge.wizard.table'].create({})
    #     return {
    #         'detail': {
    #             'modules': module_wizard.purge_line_ids.mapped('name'),
    #             'columns': column_wizard.purge_line_ids.mapped('name'),
    #             # 'data': data_wizard.purge_line_ids.mapped('name'),
    #             'menus': menu_wizard.purge_line_ids.mapped('name'),
    #             'models': model_wizard.purge_line_ids.mapped('name'),
    #             'tables': table_wizard.purge_line_ids.mapped('name'),
    #         }
    #     }

    # purge_status_state = fields.Selection([
    #     ('ok', 'OK')
    #     ],
    #     'Purge Status State',
    #     readonly=True,
    #     # default=_get_purge_status_detail,
    #     )
    # purge_status_detail = fields.Text(
    #     'Purge Status Detail',
    #     readonly=True,
    #     default=_get_purge_status_detail,
    #     )

    @api.multi
    def action_fix_db(self):
        self.fix_db(raise_msg=True)

    @api.model
    def fix_db(self, raise_msg=False):
        res = self.check_ability_to_fix(raise_msg)
        if res.get('error'):
            return res
        # if automatic backups enable, make backup
        if self.env['db.database'].check_automatic_backup_enable():
            self.backup_db()
        self.env['ir.module.module'].sudo().update_list()
        self.set_install_modules()
        self.set_uninstall_modules()
        self.set_update_modules()
        self.env['base.module.upgrade'].sudo().upgrade_module()
        # otra forma de hacerlo
        # pooler.restart_pool(self._cr.dbname, update_module=True)
        return {}

    @api.model
    def check_ability_to_fix(self, raise_msg):
        update_detail = self._get_update_detail()
        if update_detail['init_and_conf_required']:
            msg = _(
                'You can not fix db, there are some modules with "Init and '
                'Config". Please correct them manually. Modules %s: ') % (
                update_detail['init_and_conf_required'])
            if raise_msg:
                raise Warning(msg)
            return {'error': msg}
        return {}

    @api.model
    def set_uninstall_modules(self):
        not_installable_list = self._get_update_detail()['not_installable']
        uninstall_modules = self.env['ir.module.module'].search(
            [('name', 'in', not_installable_list)])
        uninstall_modules.sudo().button_uninstall()

    @api.model
    def set_install_modules(self):
        unmet_deps_list = self._get_update_detail()['unmet_deps']
        install_modules = self.env['ir.module.module'].search(
            [('name', 'in', unmet_deps_list)])
        install_modules.sudo().button_install()

    @api.model
    def set_update_modules(self):
        update_detail = self._get_update_detail()
        update_modules_list = (
            update_detail['optional_update'] +
            update_detail['update_required']
            )
        update_modules = self.env['ir.module.module'].search(
            [('name', 'in', update_modules_list)])
        update_modules.sudo().button_upgrade()

    @api.model
    def backup_db(self):
        self_database = self.env['db.database'].search(
            [('type', '=', 'self')], limit=1)
        if not self_database:
            raise Warning(_('Not Self Database Found'))
        now = datetime.now()
        backup_name = 'backup_for_fix_db_%s.zip' % (
            now.strftime('%Y%m%d_%H%M%S'))
        keep_till_date = date.strftime(
            date.today() + relativedelta(days=30), '%Y-%m-%d')
        self_database.database_backup(
            'manual',
            backup_format='zip',
            backup_name=backup_name,
            keep_till_date=keep_till_date,
            )
