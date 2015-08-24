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
        return self.get_update_state()['state']

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

    @api.model
    def get_update_state(self):
        """
        We return a dictionary with an state and for each state a list of
        modules on that state:
        * states:
            * init_and_conf_modules: modules wich version indicates that an
            init or manual operation is needed
            * update_modules: modules wich version indicates that an update
            is needed
            * optional_update_modules: modules wich version indicates that only
            a restart is enought, update only if we want version update

        """
        installed_modules = self.env['ir.module.module'].search([
            ('state', '=', 'installed')])
        init_and_conf_modules = installed_modules.filtered(
            lambda r: r.update_state == 'init_and_conf')
        update_modules = installed_modules.filtered(
            lambda r: r.update_state == 'update')
        optional_update_modules = installed_modules.filtered(
            lambda r: r.update_state == 'optional_update')

        to_upgrade_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to upgrade')])
        to_install_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to install')])
        to_remove_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to upgrade')])

        if to_upgrade_modules:
            update_state = 'modules_on_to_upgrade'
        elif to_install_modules:
            update_state = 'modules_on_to_install'
        elif to_remove_modules:
            update_state = 'modules_on_to_remove'
        elif init_and_conf_modules:
            update_state = 'init_and_conf'
        elif update_modules:
            update_state = 'update'
        elif optional_update_modules:
            update_state = 'optional_update'
        else:
            update_state = 'ok'
        return {
            'state': update_state,
            'detail': {
                'update_modules': update_modules.mapped('name'),
                'init_and_conf_modules': init_and_conf_modules.mapped('name'),
                'optional_update_modules': optional_update_modules.mapped(
                    'name'),
                'to_upgrade_modules': to_upgrade_modules.mapped('name'),
                'to_remove_modules': to_remove_modules.mapped('name'),
                'to_install_modules': to_install_modules.mapped('name'),
            }
        }
