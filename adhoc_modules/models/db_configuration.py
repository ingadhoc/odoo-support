# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class database_tools_configuration(models.TransientModel):
    _inherit = 'db.configuration'

    @api.one
    # dummy depends to get initial data
    @api.depends('backups_state')
    def get_adhoc_modules_data(self):
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
        compute='get_adhoc_modules_data',
        string='Installed Uninstallable',
    )
    installed_uncontracted_modules = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
        string='Installed Uncontracted',
    )
    not_installed_autoinstall_modules = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
        string='Not Installed Auto-Install',
    )
    not_installed_by_category_modules = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
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
