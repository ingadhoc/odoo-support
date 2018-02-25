##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
# from odoo import pooler
from odoo.exceptions import ValidationError
# from odoo.modules.registry import RegistryManager
# from datetime import datetime
# from datetime import date
# from dateutil.relativedelta import relativedelta
from odoo.addons.server_mode.mode import get_mode
import logging
_logger = logging.getLogger(__name__)


class database_tools_configuration(models.TransientModel):
    _name = 'db.configuration'
    _inherit = 'res.config.settings'

    update_detail = fields.Text(
        'Update Detail',
        readonly=True,
        compute='get_modules_data',
        # default=_get_update_detail,
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
        ('installed_uninstallable', 'Installed Uninstallable'),
        ('installed_uncontracted', 'Installed Uncontracted'),
        ('uninstalled_auto_install', 'Uninstalled Auto Install'),
    ],
        'Modules Status',
        readonly=True,
        compute='get_modules_data',
        # default=_get_update_state,
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
    installed_uninstallable_modules = fields.Many2many(
        'ir.module.module',
        compute='_compute_adhoc_modules_data',
        string='Installed Uninstallable',
    )
    installed_uncontracted_modules = fields.Many2many(
        'ir.module.module',
        compute='_compute_adhoc_modules_data',
        string='Installed Uncontracted',
    )
    not_installed_autoinstall_modules = fields.Many2many(
        'ir.module.module',
        compute='_compute_adhoc_modules_data',
        string='Not Installed Auto-Install',
    )
    not_installed_by_category_modules = fields.Many2many(
        'ir.module.module',
        compute='_compute_adhoc_modules_data',
        string='Not Installed by Categories',
    )

    @api.one
    @api.depends('update_state')
    def _compute_adhoc_modules_data(self):
        modules = self.env['ir.module.module']
        self.installed_uninstallable_modules = (
            modules._get_installed_uninstallable_modules())
        self.installed_uncontracted_modules = (
            modules._get_installed_uncontracted_modules())
        self.not_installed_autoinstall_modules = (
            modules._get_not_installed_autoinstall_modules())
        self.not_installed_by_category_modules = (
            modules._get_not_installed_by_category_modules())

    @api.multi
    def set_to_install_auto_install_modules(self):
        self.ensure_one()
        _logger.info('Setting to install auto install modules')
        return self.not_installed_autoinstall_modules._set_to_install()

    @api.multi
    def button_uninstall_uninstallable(self):
        self.ensure_one()
        _logger.info('Setting to uninstall uninstallable modules')
        return self.installed_uninstallable_modules._set_to_uninstall()
        # return self.installed_uninstallable_modules.button_uninstall()

    @api.model
    def _cron_update_adhoc_modules(self):
        if get_mode():
            _logger.info(
                'Update adhoc modules is disable by server_mode. '
                'If you want to enable it you should remove develop or test '
                'value for server_mode key on openerp server config file')
            return False
        try:
            self.get_adhoc_modules_data()
        except Exception as e:
            _logger.error(
                "Error Updating ADHOC Modules Data. Error:\n%s" % (e))

    @api.multi
    def get_adhoc_modules_data(self):
        # TODO cuando no usemos mas web support que daria solo esta parte
        # y agregamos dependencia a saas_client
        # if saas_client is installed:
        if self.env['ir.module.module'].search([
                ('name', '=', 'saas_client')]).state == 'installed':
            self.env['saas_client.dashboard'].get_adhoc_modules_data()
            return True
        elif self.env['ir.module.module'].search([
                ('name', '=', 'adhoc_modules_web_support')]
        ).state == 'installed':
            contract = self.env['support.contract'].get_active_contract()
            contract.get_active_contract().get_adhoc_modules_data()
            return True
        raise ValidationError(_(
            'You should install "saas_client" or "adhoc_modules_web_support"'))

    @api.one
    # dummy depends to get initial data
    # TODO fix this, it can not depends on same field
    # @api.depends('update_state')
    def get_modules_data(self):
        overal_state = self.env[
            'ir.module.module'].with_context(
                called_locally=True).get_overall_update_state()
        self.update_state = overal_state['state']
        self.update_detail = overal_state['detail']
        modules_state = overal_state['modules_state']
        # modules_state = self.env['ir.module.module']._get_modules_state()
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
        """
        Si lo hacemos por interfaz entonces si forzamos la desinstalacion
        porque esto es manual
        """
        self.fix_db(raise_msg=True, uninstall_modules=True)

    @api.model
    def fix_db(
            self, raise_msg=False,
            uninstall_modules=False):
        """
        Desde el cron:
        1. para no mandarnos errores, no desintalamos ningun modulo
        podria pasar de que falta un repo y borramos mucha data (los script
        de los modulos deberianser quien se encarguen de limpiar)
        2. solo actualizamos si hay modulos que requiran update o dependencias
        faltantes
        """
        # because we make methods with api multi and we use a computed field
        # we need an instance of this class to run some methods

        # TODO tal vez deberiamos ahcer que unmet_deps no sea campo m2m porque
        # si la dependencia es nueva y no se actualiza en el modulo con nueva
        # dependencia la version, entonces el update state va a devolver ok
        # ya que el modulo no es visto por el orm, el problema esta en la
        # funcion _get_modules_state que hacemos un search, deberiamos
        # directamente devolver los nombres. Igualmente, si al modulo se le
        # cambia la version, se actualiza la lista de modulos y el invalidate
        # cache hace que sea visible
        self = self.create({})

        update_state = self.update_state

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
                raise ValidationError(error_msg)
            _logger.info(error_msg)
            return {'error': error_msg}

        _logger.info('Fixing database')

        # if automatic backups enable, make backup
        # we use pg_dump to make backups quickly
        # TODO reactvamos esto? lo sacamos por ahora porque no usamos
        # mas el db tools
        # if self.env['db.database'].check_automatic_backup_enable():
        #     self.backup_db(backup_format='pg_dump')

        _logger.info('Updating modules list')
        self.env['ir.module.module'].sudo().update_list()
        # necesario para que unmet deps y otros se actualicen con nuevos
        # modulos
        self.invalidate_cache()
        _logger.info('Modules list updated')

        self.set_to_install_unmet_deps()

        if uninstall_modules:
            self.set_to_uninstall_not_installable_modules()

        self.set_to_update_required_modules()
        self.set_to_update_optional_modules()
        self.set_to_update_init_and_conf_required_modules()

        # no estoy seguro porque pero esto ayuda a que no quede trabado cuando
        # llamamos a upgrade_module
        # save before re-creating cursor below on upgrade
        self._cr.commit()  # pylint: disable=invalid-commit
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

        if uninstall_modules:
            # borramos los registros de modulos viejos para que no jodan
            # to install, necesitamos el commit para tener cambio de estado
            self.env.cr.commit()  # pylint: disable=invalid-commit
            self.not_installable_modules.sudo().unlink()
        # otra forma de hacerlo
        # pooler.restart_pool(self._cr.dbname, update_module=True)
        # interesante para analizar esto
        # odoo.modules.registry.Registry.new(
        #     cr.dbname, update_module=True)
        return {}

    @api.multi
    def clean_todo_list(self):
        return self.env['base.module.upgrade'].upgrade_module_cancel()

    @api.multi
    def set_to_uninstall_not_installable_modules(self):
        _logger.info('Fixing not installable')
        self.installed_uninstallable_modules.sudo()._set_to_uninstall()
        self.not_installable_modules.sudo()._set_to_uninstall()
        return True

    @api.multi
    def set_to_install_unmet_deps(self):
        _logger.info('Fixing unmet dependencies')
        self.not_installed_autoinstall_modules.sudo()._set_to_install()
        self.unmet_deps_modules.sudo()._set_to_install()
        return True

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

    # @api.model
    # def backup_db(self, backup_format):
    #     self_database = self.env['db.database'].search(
    #         [('type', '=', 'self')], limit=1)
    #     if not self_database:
    #         raise ValidationError(_('Not Self Database Found'))
    #     now = datetime.now()
    #     backup_name = 'backup_for_fix_db_%s.%s' % (
    #         now.strftime('%Y%m%d_%H%M%S'), backup_format)
    #     keep_till_date = date.strftime(
    #         date.today() + relativedelta(days=30), '%Y-%m-%d')
    #     self_database.database_backup(
    #         'manual',
    #         backup_format=backup_format,
    #         backup_name=backup_name,
    #         keep_till_date=keep_till_date,
    #     )
