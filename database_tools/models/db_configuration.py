# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class database_tools_configuration(models.TransientModel):
    _name = 'db.configuration'
    _inherit = 'res.config.settings'

    @api.model
    def _get_update_state(self):
        return self.env['ir.module.module'].get_overall_update_state()['state']

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
        readonly=True,
        default=_get_backups_state,
        )
    backups_detail = fields.Text(
        readonly=True,
        default=_get_backups_detail,
        )
    update_state = fields.Selection([
        ('init_and_conf', 'Init and Config'),
        ('update', 'Update'),
        ('optional_update', 'Optional Update'),
        ('to_install_modules', 'Modules on To Install'),
        ('to_remove_modules', 'Modules on To Remove'),
        ('to_upgrade_modules', 'Modules on To Upgrade'),
        ('ok', 'Ok'),
        ],
        'Update Status',
        readonly=True,
        default=_get_update_state,
        # store=True,
        )
