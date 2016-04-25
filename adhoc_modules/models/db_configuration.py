# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from openerp.addons.adhoc_modules.models.ir_module import uninstallables
# from openerp.exceptions import Warning
# from datetime import datetime
# from datetime import date
# from dateutil.relativedelta import relativedelta


class database_tools_configuration(models.TransientModel):
    _inherit = 'db.configuration'

    # @api.model
    # def _get_adhoc_modules_state(self):
    #     return self.env[
    #         'ir.module.module'].get_overall_adhoc_modules_state()['state']

    @api.one
    # dummy depends son computed field is computed
    @api.depends('backups_state')
    def get_adhoc_modules_data(self):
        uninstalled_modules_names = self.env['ir.module.module'].search([
            ('state', 'not in', ['installed', 'to install'])]).mapped('name')
        auto_install_modules = self.env['ir.module.module'].search([
            # '|', ('dependencies_id', '=', False),
            ('dependencies_id.name', 'not in', uninstalled_modules_names),
            ('conf_visibility', '=', 'auto_install'),
            ('state', '=', 'uninstalled'),
        ])
        self.adhoc_modules_to_install = auto_install_modules
        self.adhoc_modules_to_uninstall = self.env['ir.module.module'].search([
            ('conf_visibility', 'in', uninstallables),
            # ('conf_visibility', 'in', []),
            ('state', '=', 'installed'),
        ])

    adhoc_modules_to_uninstall = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
    )
    adhoc_modules_to_install = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
    )
    # adhoc_modules_state = fields.Selection([
    #     ('should_not_be_installed', 'Should Not be Installed'),
    #     ('installation_required', 'Installation Required'),
    #     ('ok', 'Ok'),
    # ],
    #     'Update Status',
    #     readonly=True,
    #     default=_get_adhoc_modules_state,
    # )