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

    installed_uninstallable_modules = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_data',
    )
