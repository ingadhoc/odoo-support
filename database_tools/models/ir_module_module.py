# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, fields
import logging
_logger = logging.getLogger(__name__)


class ir_module_module(models.Model):
    _inherit = "ir.module.module"

    update_state = fields.Selection([
        ('init_and_conf', 'Init and Config'),
        ('update', 'Update'),
        ('optional_update', 'Optional Update'),
        ('modules_on_to_install', 'Modules on To Install'),
        ('modules_on_to_remove', 'Modules on To Remove'),
        ('modules_on_to_upgrade', 'Modules on To Upgrade'),
        ('ok', 'Ok'),
        ],
        'Update Status',
        compute='get_update_state',
        )

    @api.one
    @api.depends('installed_version', 'latest_version')
    def get_update_state(self):
        """
        We use version number Guidelines x.y.z from
        https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md#version-numbers
        """
        update_state = 'ok'
        # installed is module avaiable version
        # latest is the module installed version
        if self.installed_version and self.latest_version:
            (ix, iy, iz) = self.get_versions(self.installed_version)
            (lx, ly, lz) = self.get_versions(self.latest_version)
            if ix > lx:
                update_state = 'init_and_conf'
            elif ix == lx and iy > ly:
                update_state = 'update'
            elif ix == lx and iy == ly and iz > lz:
                update_state = 'optional_update'
        self.update_state = update_state

    @api.model
    def get_versions(self, version):
        # split by '.'
        version_list = version.split('.')

        # we take out mayor version, and take only 3 elements
        minor_version = version_list[2:5]

        # fill sufix with ceros till we get three elements
        minor_version += ['0'] * (3 - len(minor_version))

        # fill everthing to 8 string character for numeric comparison
        return [x.zfill(8) for x in minor_version]

    # older version that use odoo parse_version but sometimes we could not
    # compare *final or other conventions
    # @api.model
    # def get_versions(self, version):
    #     # we take out mayor version
    #     parsed = list(parse_version(version)[2:])
    #     x = parsed and parsed.pop(0) or False
    #     y = parsed and parsed.pop(0) or False
    #     z = parsed and parsed.pop(0) or False
    #     return (x, y, z)

    @api.model
    def get_overall_update_state(self):
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
        installed_modules = self.search([
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
