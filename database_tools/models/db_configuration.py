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
from openerp.service.server import restart
import logging
_logger = logging.getLogger(__name__)


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

    restart = fields.Boolean()
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
    def fix_db_cron(self):
        _logger.info('Running fix db cron')
        self.fix_db(False, False, True)
        # TODO terminar de implementar restart_if_needed
        # no lo usamos porque al trabajar sin workers la instancia no
        # vuelve a levantar y además porque con varias bds en una instancia se
        # reiniciaria muchas veces la instancia, ademas es probable que
        # haciendo que los repos esten con docker no se necesite
        return True

    @api.model
    def fix_db(
            self, raise_msg=False,
            uninstall_modules=True, restart_if_needed=False):
        """
        Desde el cron:
        1. para no mandarnos errores, no desintalamos ningun modulo
        podria pasar de que falta un repo y borramos mucha data
        2. solo actualizamos si hay modulos que requiran update o dependencias
        faltantes
        NOTA: por ahora restart_if_needed lo usa solo el cron y el cron
        ademas esta deshabilitado
        """
        # check if urgent and update status
        overall_state = self.env['ir.module.module'].get_overall_update_state()
        update_state = overall_state['state']
        update_detail = overall_state['detail']

        error_msg = False
        if update_state == 'ok':
            error_msg = 'No need to fix db'
        elif update_detail['init_and_conf_required']:
            error_msg = _(
                'You can not fix db, there are some modules with "Init and '
                'Config". Please correct them manually. Modules %s: ') % (
                update_detail['init_and_conf_required'])

        if error_msg:
            if raise_msg:
                raise Warning(error_msg)
            _logger.info(error_msg)
            return {'error': error_msg}
        _logger.info('Fixing database')

        parameters = self.env['ir.config_parameter']
        if restart_if_needed:
            just_restart = parameters.get_param('just_restart')
            if just_restart:
                just_restart = eval(just_restart)
            if not just_restart:
                parameters.set_param('just_restart', 'True')
                self._cr.commit()
                restart()
        parameters.set_param('just_restart', 'False')

        self.fix_optional_update_modules()

        # # if only update_optional then we don not make backup
        if (
                not update_detail['unmet_deps'] and
                not update_detail['update_required'] and
                not (update_detail['not_installable'] and uninstall_modules)):
            return {}
        # if automatic backups enable, make backup
        if self.env['db.database'].check_automatic_backup_enable():
            self.backup_db()

        self.env['ir.module.module'].sudo().update_list()
        self.set_install_modules()

        if uninstall_modules:
            self.set_uninstall_modules()
        self.set_update_modules()
        self.env['base.module.upgrade'].sudo().upgrade_module()
        # otra forma de hacerlo
        # pooler.restart_pool(self._cr.dbname, update_module=True)
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
    def fix_optional_update_modules(self):
        # we only update version nunmber
        _logger.info('Fixing optional update modules')
        update_detail = self._get_update_detail()
        optional_update_modules = self.env['ir.module.module'].search(
            [('name', 'in', update_detail['optional_update'])])
        for module in optional_update_modules:
            module.sudo().latest_version = module.installed_version

    @api.model
    def set_update_modules(self):
        _logger.info('Fixing update modules')
        update_detail = self._get_update_detail()
        update_modules = self.env['ir.module.module'].search(
            [('name', 'in', update_detail['update_required'])])
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
