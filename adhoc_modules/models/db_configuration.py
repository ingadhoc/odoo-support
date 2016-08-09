# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
# from openerp.addons.adhoc_modules.models.ir_module import uninstallables
# from openerp.exceptions import Warning
# from datetime import datetime
# from datetime import date
# from dateutil.relativedelta import relativedelta


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
    )
    installed_uncontracted_modules = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
    )
    not_installed_autoinstall_modules = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
    )
    not_installed_by_category_modules = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
    )

    @api.multi
    def set_to_install_auto_install_modules(self):
        self.ensure_one()
        return self.not_installed_autoinstall_modules._set_to_install()
    # update_state = fields.Selection(
    #     selection_add=[('modules_error', 'Modules Error')],
    # )
