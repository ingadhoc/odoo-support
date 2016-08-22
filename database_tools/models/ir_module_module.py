# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, fields, modules
import openerp.tools as tools
import logging
_logger = logging.getLogger(__name__)


class ir_module_module(models.Model):
    _inherit = "ir.module.module"

    # this is the status of only one module
    update_state = fields.Selection([
        ('init_and_conf_required', 'Init and Config'),
        ('update_required', 'Update'),
        ('optional_update', 'Optional Update'),
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
                update_state = 'init_and_conf_required'
            elif ix == lx and iy > ly:
                update_state = 'update_required'
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
    def get_update_required(self):
        return self.search([('state', '=', 'installed')]).filtered(
            lambda r: r.update_state == 'update_required')

    @api.model
    def get_optional_update(self):
        return self.search([('state', '=', 'installed')]).filtered(
            lambda r: r.update_state == 'optional_update')

    @api.model
    def get_overall_update_state(self):
        """
        We return a dictionary with an state and for each state a list of
        modules on that state:
        * states:
            * init_and_conf_required: modules wich version indicates that an
            init or manual operation is needed
            * update_required: modules wich version indicates that an update
            is needed
            * optional_update: modules wich version indicates that only
            a restart is enought, update only if we want version update

        """
        modules_availabilty = self.get_modules_availabilty()
        unmet_deps = modules_availabilty['unmet_deps']
        not_installable = modules_availabilty['not_installable']

        installed_modules = self.search([('state', '=', 'installed')])
        # because not_installable version could be miss understud as
        # init_and_conf_required, we remove them from this list
        init_and_conf_required = installed_modules.filtered(
            lambda r: r.update_state == 'init_and_conf_required' and
            r.name not in not_installable)
        # update_required = installed_modules.filtered(
        #     lambda r: r.update_state == 'update_required')
        # optional_update = installed_modules.filtered(
        #     lambda r: r.update_state == 'optional_update')
        update_required = self.get_update_required()
        optional_update = self.get_optional_update()

        to_upgrade_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to upgrade')])
        to_install_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to install')])
        to_remove_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to upgrade')])

        if not_installable:
            update_state = 'not_installable'
        elif unmet_deps:
            update_state = 'unmet_deps'
        elif to_upgrade_modules:
            update_state = 'on_to_upgrade'
        elif to_install_modules:
            update_state = 'on_to_install'
        elif to_remove_modules:
            update_state = 'on_to_remove'
        elif init_and_conf_required:
            update_state = 'init_and_conf_required'
        elif update_required:
            update_state = 'update_required'
        elif optional_update:
            update_state = 'optional_update'
        else:
            update_state = 'ok'
        return {
            'state': update_state,
            'detail': {
                'init_and_conf_required': init_and_conf_required.mapped(
                    'name'),
                'update_required': update_required.mapped('name'),
                'optional_update': optional_update.mapped(
                    'name'),
                'on_to_upgrade': to_upgrade_modules.mapped('name'),
                'on_to_remove': to_remove_modules.mapped('name'),
                'on_to_install': to_install_modules.mapped('name'),
                'unmet_deps': unmet_deps,
                'not_installable': not_installable,
            }
        }

    @api.model
    def get_modules_availabilty(self):
        states = ['installed', 'to upgrade', 'to remove', 'to install']
        force = []
        packages = []
        not_installable = []
        unmet_deps = []
        graph = modules.graph.Graph()

        modules_list = self.search([('state', 'in', states)]).mapped('name')
        if not modules:
            return True

        for module in modules_list:
            info = modules.module.load_information_from_description_file(
                module)
            if info and info['installable']:
                packages.append((module, info))
            else:
                not_installable.append(module)

        dependencies = dict([(p, info['depends']) for p, info in packages])
        current, later = set([p for p, info in packages]), set()

        while packages and current > later:
            package, info = packages[0]
            deps = info['depends']

            # if all dependencies of 'package' are already in the graph,
            # add 'package' in the graph
            if reduce(lambda x, y: x and y in graph, deps, True):
                if package not in current:
                    packages.pop(0)
                    continue
                later.clear()
                current.remove(package)
                node = graph.add_node(package, info)
                for kind in ('init', 'demo', 'update'):
                    if (
                            package in tools.config[kind] or
                            'all' in tools.config[kind] or kind in force
                            ):
                        setattr(node, kind, True)
            else:
                later.add(package)
                packages.append((package, info))
            packages.pop(0)

        for package in later:
            unmet_deps += filter(
                lambda p: p not in graph, dependencies[package])
        unmet_deps = list(set(unmet_deps))
        # remove from unmet_deps modules that are installed but can not be
        # loaded because of unmet deps
        unmet_deps = filter(lambda x: x not in modules_list, unmet_deps)
        return {
            'unmet_deps': unmet_deps,
            'not_installable': not_installable
        }

# methods that not apply inemdiatlelly

    @api.multi
    def button_set_to_install(self):
        """
        Boton que devuelve wizar di hay dependencias y si no los pone a
        instalar.
        Ademas usa el _set_to_install en vez de button_install
        """
        # self.ensure_one()
        deps = self.mapped('dependencies_id.depend_id')
        uninstalled_deps = deps.filtered(lambda x: x.state == 'uninstalled')
        if uninstalled_deps:
            action = self.env['ir.model.data'].xmlid_to_object(
                'adhoc_modules.action_base_module_pre_install')

            if not action:
                return False
            res = action.read()[0]
            res['context'] = {
                'default_dependency_ids': uninstalled_deps.ids,
                'default_module_id': self.id,
            }
            return res
        return self._set_to_install()

    @api.multi
    def _set_to_install(self):
        """
        Igual que button install pero no ejecuta automaticamente (ni devuelve
        wizard)
        """
        super(ir_module_module, self).button_install()
        # # Mark the given modules to be installed.
        # self.state_update('to install', ['uninstalled'])

        # # Select all auto-installable (but not yet installed) modules
        # to_install_modules = self._get_to_install_autoinstall_modules()

        # # Mark them to be installed.
        # if to_install_modules:
        #     to_install_modules.button_install()

        return True

    @api.multi
    def _set_to_uninstall(self):
        """
        Igual que button uninstall pero no ejecuta automaticamente (ni devuelve
        wizard)
        """
        super(ir_module_module, self).button_uninstall()
        return True
        # # self.ensure_one()
        # if 'base' in self.mapped('name'):
        #     raise Warning(_("The `base` module cannot be uninstalled"))
        # dep_ids = self.downstream_dependencies()
        # to_uninstall = self + self.browse(dep_ids)
        # to_uninstall.write({'state': 'to remove'})

    @api.multi
    def _set_to_upgrade(self):
        """
        Igual que button upgrade pero no ejecuta automaticamente (ni devuelve
        wizard)
        """
        super(ir_module_module, self).button_upgrade()
        return True

        # self.ensure_one()
        # depobj = self.env['ir.module.module.dependency']
        # todo = list(self)
        # self.update_list()

        # i = 0
        # while i < len(todo):
        #     mod = todo[i]
        #     i += 1
        #     if mod.state not in ('installed', 'to upgrade'):
        #         raise Warning(_(
        #             "Can not upgrade module '%s'. It is not installed.") % (
        #             mod.name,))
        #     self.check_external_dependencies(mod.name, 'to upgrade')
        #     deps = depobj.search([('name', '=', mod.name)])
        #     for dep in deps:
        #         if dep.module_id.state == 'installed' and dep.module_id not in todo:
        #             todo.append(dep.module_id)

        # ids = map(lambda x: x.id, todo)
        # self.browse(ids).write({'state': 'to upgrade'})

        # to_install = []
        # for mod in todo:
        #     for dep in mod.dependencies_id:
        #         if dep.state == 'unknown':
        #             raise Warning(_(
        #                 'You try to upgrade a module that depends on the module: %s.\nBut this module is not available in your system.') % (dep.name,))
        #         if dep.state == 'uninstalled':
        #             ids2 = self.search([('name', '=', dep.name)])
        #             to_install.extend(ids2.id)

        # self.browse(to_install).button_set_to_install()
        # return True
        # # return dict(ACTION_DICT, name=_('Apply Schedule Upgrade'))
