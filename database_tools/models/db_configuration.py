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
        'Modules Status',
        readonly=True,
        default=_get_update_state,
    )
    init_and_conf_required_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
    )
    update_required_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
        string='Update Required',
    )
    optional_update_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
        string='Optional Update',
    )
    to_remove_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
        string='To Remove',
    )
    to_install_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
        string='To Install',
    )
    to_upgrade_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
        string='To Upgrade',
    )
    unmet_deps_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
        string='Unmet Dependencies',
    )
    not_installable_modules = fields.Many2many(
        'ir.module.module',
        compute='get_modules_data',
        string='Not Installable',
    )

    @api.one
    # dummy depends to get initial data
    @api.depends('backups_state')
    def get_modules_data(self):
        modules_state = self.env['ir.module.module']._get_modules_state()
        self.init_and_conf_required_modules = modules_state.get(
            'init_and_conf_required')
        self.update_required_modules = modules_state.get('update_required')
        self.optional_update_modules = modules_state.get('optional_update')
        self.unmet_deps_modules = modules_state.get('unmet_deps')
        self.not_installable_modules = modules_state.get('not_installable')
        self.to_upgrade_modules = modules_state.get('to_upgrade_modules')
        self.to_install_modules = modules_state.get('to_install_modules')
        self.to_remove_modules = modules_state.get('to_remove_modules')

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
        # because we make methods with api multi and we use a computed field
        # we need an instance of this class to run some methods
        self = self.create({})

        # check if urgent and update status
        overall_state = self.env['ir.module.module'].get_overall_update_state()
        update_state = overall_state['state']
        update_detail = overall_state['detail']

        error_msg = False
        if update_state == 'ok':
            error_msg = 'No need to fix db'
        # elif update_detail['init_and_conf_required']:
        #     error_msg = _(
        #         'You can not fix db, there are some modules with "Init and '
        #         'Config". Please correct them manually. Modules %s: ') % (
        #         update_detail['init_and_conf_required'])

        # if anything to fix, we exit
        if error_msg:
            if raise_msg:
                raise Warning(error_msg)
            _logger.info(error_msg)
            return {'error': error_msg}

        _logger.info('Fixing database')

        parameters = self.env['ir.config_parameter']
        # por ahorano se esta usando
        if restart_if_needed:
            just_restart = parameters.get_param('just_restart')
            if just_restart:
                just_restart = eval(just_restart)
            if not just_restart:
                parameters.set_param('just_restart', 'True')
                self._cr.commit()
                restart()
        parameters.set_param('just_restart', 'False')

        # if automatic backups enable, make backup
        if self.env['db.database'].check_automatic_backup_enable():
            self.backup_db()

        _logger.info('Updating modules list')
        self.env['ir.module.module'].sudo().update_list()
        _logger.info('Modules list updated')
        self.set_to_install_unmet_deps()

        if uninstall_modules:
            self.set_to_uninstall_not_installable_modules()

        self.set_to_update_required_modules()
        self.set_to_update_optional_modules()
        self.set_to_update_init_and_conf_required_modules()

        # save before re-creating cursor below on upgrade
        self._cr.commit()
        modules = self.env['ir.module.module']
        _logger.info(
            'Runing upgrade module.\n'
            '* Modules to upgrade: %s\n'
            '* Modules to install: %s\n'
            '* Modules to remove: %s' % (
                modules.search([('state', '=', 'to upgrade')]).mapped('name'),
                modules.search([('state', '=', 'to install')]).mapped('name'),
                modules.search([('state', '=', 'to remove')]).mapped('name'),
            ))
        self.env['base.module.upgrade'].sudo().upgrade_module()
        _logger.info('Upgrade module finished')
        # otra forma de hacerlo
        # pooler.restart_pool(self._cr.dbname, update_module=True)
        # interesante para analizar esto
        # openerp.modules.registry.RegistryManager.new(
        #     cr.dbname, update_module=True)
        return {}

    @api.multi
    def clean_todo_list(self):
        return self.env['base.module.upgrade'].upgrade_module_cancel()

    @api.multi
    def set_to_uninstall_not_installable_modules(self):
        _logger.info('Fixing not installable')
        return self.not_installable_modules.sudo()._set_to_uninstall()

    @api.multi
    def set_to_install_unmet_deps(self):
        _logger.info('Fixing unmet dependencies')
        return self.unmet_deps_modules.sudo()._set_to_install()

    @api.multi
    def set_to_update_optional_modules(self):
        _logger.info('Fixing optional update modules')
        return self.optional_update_modules.sudo()._set_to_upgrade()

    @api.multi
    def set_to_update_required_modules(self):
        _logger.info('Fixing update required modules')
        return self.update_required_modules.sudo()._set_to_upgrade()

    @api.multi
    def set_to_update_init_and_conf_required_modules(self):
        _logger.info('Fixing update required modules')
        return self.init_and_conf_required_modules.sudo()._set_to_upgrade()

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
