# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.server_mode.mode import get_mode
import logging
_logger = logging.getLogger(__name__)


class database_tools_configuration(models.TransientModel):
    _inherit = 'db.configuration'

    @api.one
    # dummy depends to get initial data
    @api.depends('backups_state')
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

    update_state = fields.Selection(
        selection_add=[
            ('installed_uninstallable', 'Installed Uninstallable'),
            ('installed_uncontracted', 'Installed Uncontracted'),
            ('uninstalled_auto_install', 'Uninstalled Auto Install'),
        ]
    )

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
        except Exception, e:
            _logger.error(
                "Error Updating ADHOC Modules Data. Error:\n%s" % (e))

    @api.multi
    def get_adhoc_modules_data(self):
        # TODO cuando no usemos mas web support que daria solo esta parte
        # y agregamos dependencia a saas_client
        # if saas_client is installed:
        if self.env['ir.module.module'].search([
                ('name', '=', 'saas_client')]).state == 'installed':
            self.env.user.post_request_on_saas_provider(
                '/saas_provider/get_modules_data')
            return True
        elif self.env['ir.module.module'].search([
                ('name', '=', 'adhoc_modules_web_support')]
        ).state == 'installed':
            contract = self.env['support.contract'].get_active_contract()
            contract.get_active_contract().get_adhoc_modules_data()
            return True
        raise ValidationError(_(
            'You should install "saas_client" or "adhoc_modules_web_support"'))

    @api.multi
    def set_to_install_unmet_deps(self):
        """
        We inherit this function to install auto install modules
        """
        res = super(
            database_tools_configuration, self).set_to_install_unmet_deps()
        _logger.info('Fixing auto install modules by adhoc modules')
        self.not_installed_autoinstall_modules.sudo()._set_to_install()
        return res

    @api.multi
    def set_to_uninstall_not_installable_modules(self):
        """
        We inherit this function to install auto install modules
        """
        res = super(
            database_tools_configuration,
            self).set_to_uninstall_not_installable_modules()
        _logger.info('Fixing not installable modules by adhoc modules')
        self.installed_uninstallable_modules.sudo()._set_to_uninstall()
        return res
