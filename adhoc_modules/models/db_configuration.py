# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
# from openerp import pooler
# from openerp.exceptions import Warning
# from datetime import datetime
# from datetime import date
# from dateutil.relativedelta import relativedelta


class database_tools_configuration(models.TransientModel):
    _inherit = 'db.configuration'

    @api.model
    def _get_adhoc_modules_state(self):
        return self.env['ir.module.module'].get_overall_adhoc_modules_state()['state']

    @api.one
    def get_adhoc_modules_to_install(self):
        print '1111111111'
        self.adhoc_modules_to_install = self.env['ir.module.module'].search([], limit=10)

    adhoc_modules_to_install = fields.Many2many(
        'ir.module.module',
        compute='get_adhoc_modules_to_install',
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