##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields, modules, tools, _
from odoo.exceptions import ValidationError
from ast import literal_eval
from odoo.addons.base.module.module import Module
import logging
from functools import reduce

_logger = logging.getLogger(__name__)
uninstallables = ['to_review', 'future_versions', 'unusable']
# installables = ['to_review', 'future_versions', 'unusable']
not_installed = ['uninstalled', 'uninstallable', 'to install']
installed = ['installed', 'to install', 'to upgrade']
# installed = ['installed', 'to upgrade', 'to remove']

# because we could not inherit button_install in classic way

button_install_original = Module.button_install


@api.multi
def button_install(self):
    # we add this check if modules are uninstallable so we can raise an error
    # by default, modules is not installed but user dont understand why
    def check_uninstallable(modules):
        newstate = 'to install'
        for mod in modules:
            for dep in mod.dependencies_id:
                if dep.state == 'uninstallable':
                    raise ValidationError(_(
                        "Error! You try to install module '%s' that depends on"
                        " module '%s'.\nBut the latter module is uninstallable"
                        " in your system.") % (mod.name, dep.name,))
                if dep.depend_id.state != newstate:
                    check_uninstallable(dep.depend_id)

    check_uninstallable(self)
    # check_incompatible_depens(self)

    # we send to install ignored dependencies
    self._state_update('to install', ['ignored'])

    # # Mark the given modules to be installed.
    # self.state_update('to install', ['uninstalled'])

    # # Mark (recursively) the newly satisfied modules to also be installed

    # # Select all auto-installable (but not yet installed) modules.
    # domain = [('state', '=', 'uninstalled'), ('auto_install', '=', True)]
    # uninstalled_ids = self.search(domain)
    # uninstalled_modules = self.browse(uninstalled_ids)

    # # Keep those with:
    # #  - all dependencies satisfied (installed or to be installed),
    # #  - at least one dependency being 'to install'
    # satisfied_states = frozenset(('installed', 'to install', 'to upgrade'))

    # def all_depencies_satisfied(m):
    #     states = set(d.state for d in m.dependencies_id)
    #     return states.issubset(satisfied_states) and ('to install' in states)
    # to_install_modules = filter(all_depencies_satisfied, uninstalled_modules)
    # to_install_ids = map(lambda m: m.id, to_install_modules)

    # # Mark them to be installed.
    # if to_install_ids:
    #     self.button_install(to_install_ids)

    return button_install_original(self)


Module.button_install = button_install


class IrModuleModule(models.Model):

    _inherit = 'ir.module.module'
    # nos parece mas facil ver el nombre tecnico directamente, ayuda mucho
    # en los m2m_tags
    _rec_name = 'name'
    _order = 'review desc,technically_critical desc,support_type,sequence,name'

    # because default sequence is overwrited every time we update module list
    # we create a new sequence field
    # era complicado agregar este campo porque empieza a dar errores y no
    # podemos actualizar, vamos a probar usando sequence por defecto de odoo
    # haria falta luego de actualizar lista de modulos refrescar desde adhoc
    # o al menos tener copiado este campo
    # si volvemos a agregar este campo entonces deberiamos
    # cambiar para que sea este quien se actualice
    # new_sequence = fields.Integer(
    #     'New Sequence',
    #     default='100'
    # )
    @api.multi
    @api.depends('incompatible_modules')
    def _compute_incompatible_modules(self):
        for rec in self:
            if not rec.incompatible_modules:
                continue
            try:
                module_names = literal_eval(rec.incompatible_modules)
                rec.incompatible_module_ids = rec.search(
                    [('name', 'in', module_names)])
            except Exception:
                continue

    incompatible_modules = fields.Char(
        readonly=True,
        help='''You mast set a list of modules as for eg as this:
        "['sale','purchase']"'''
    )
    incompatible_module_ids = fields.Many2many(
        'ir.module.module',
        compute='_compute_incompatible_modules',
        string='Incompatible Modules',
    )
    adhoc_category_id = fields.Many2one(
        'adhoc.module.category',
        'ADHOC Category',
        auto_join=True,
        readonly=True,
    )
    computed_summary = fields.Char(
        compute='_compute_computed_summary',
        inverse='_inverse_adhoc_summary',
        readonly=True,
    )
    adhoc_summary = fields.Char(
        readonly=True,
    )
    adhoc_description_html = fields.Html(
        readonly=True,
    )
    support_type = fields.Selection([
        ('supported', 'Soportado'),
        ('unsupported', 'No Soportado'),
        # ('unsupport_all', 'No Soporta BD'),
    ],
        string='Support Type',
        readonly=True,
        # no lo hacemos required aca porque es un poco delicado y nos da error
        # al actualizar, lo hacemos en server, deberiamos hacer por script
        # de migracion que setee este valor y ahí si lo ponemos
        # required=True,
        default='unsupported',
    )
    technically_critical = fields.Boolean(
        readonly=True,
        # agregamos default para que se ordenen correctamente porque es
        # distinto a vacio
        default=False,
    )
    review = fields.Selection([
        ('0', 'Not Recommended'),
        ('1', 'Only If Necessary'),
        ('2', 'Neutral'),
        ('3', 'Recommended'),
        ('4', 'Highly Recommended'),
    ], 'Review',
        index=True,
        readonly=True,
        default='0',
    )
    conf_visibility = fields.Selection([
        # instalables
        ('normal', 'Manual'),
        # auto install va a setear auto_install de odoo
        ('auto_install', 'Auto Instalar por Dep.'),
        ('auto_install_by_code', 'Auto Instalado por Cód.'),
        # auto install va a marcar to install si categoria contratada
        ('auto_install_by_categ', 'Auto Instalar por Cat.'),
        # estos dos no son visibles de manera predeterminada
        ('installed_by_others', 'Instalado por Otro'),
        ('on_config_wizard', 'En asistente de configuración'),
        # no instalable
        ('to_review', 'A Revisar'),
        ('future_versions', 'Versiones Futuras'),
        ('unusable', 'No Usable'),
    ],
        'Visibility',
        # no lo hacemos required aca porque es un poco delicado y nos da error
        # al actualizar, lo hacemos en server
        readonly=True,
        # no le ponemos por defecto to_review porque es muy fuerte y los
        # hace no instalables de entrada
        default='normal',
        help="Módulos que se pueden instalar:\n"
        "* Manual: debe seleccionar manualmente si desea intalarlo\n"
        # "* Solo si dep.: se muestra solo si dependencias instaladas\n"
        "* Auto Instalar por Dep.: auto instalar si se cumplen dependencias\n"
        "* Auto Instalado por Código: auto instalado si se cumplen "
        "dependencias\n"
        "* Auto Instalar por Cat.: auto instalar si se categoría contratada\n"
        "* Auto Instalado Por Módulo: se instala si se cumplen dependencias\n"
        "* Instalado por Otro: algún otro módulo dispara la instalación\n"
        "* En asistente de configuración: este módulo esta presente en el "
        "asistente de configuración\n"
        "\nMódulos en los que se bloquea la instalación:\n"
        "* A Revisar: hay que analizar como lo vamos a utilizar\n"
        "* Versiones Futuras: se va a incorporar más adelante\n"
        "* No Usable: no se usa ni se va a sugerir uso en versiones futuras\n"
    )
    visibility_obs = fields.Char(
        'Visibility Observation',
        readonly=True,
    )
    # visible = fields.Boolean(
    #     compute='_compute_visible',
    #     search='search_visible',
    # )
    state = fields.Selection(
        selection_add=[('ignored', 'Ignored')]
    )

    @api.constrains('state')
    def check_compatibility(self):
        # si seteamos un modulo a instalar, chequeamos dependencias
        if self.state == 'to install' and self.incompatible_module_ids:
            incompatible_modules = self.search([
                ('state', 'in', installed),
                ('id', 'in', self.incompatible_module_ids.ids),
            ])
            if incompatible_modules:
                raise ValidationError(_(
                    'You can not install module "%s" as you have this '
                    'incompatible dependencies installed: %s') % (
                    self.name, incompatible_modules.mapped('name')))

    @api.constrains('state')
    def check_contracted(self):
        # we keep this just in case some module was not set in "uninstallable"
        # state
        if (
                self.state == 'to install' and
                self.adhoc_category_id and
                not self.adhoc_category_id.contracted):
            raise ValidationError(_(
                'You can not install module "%s" as category "%s" is not '
                'contracted') % (self.name, self.adhoc_category_id.name))

    @api.model
    def update_list(self):
        res = super(IrModuleModule, self).update_list()
        # TODO, hasta que no lo hagamos mas eficiente solo lo vamos a hacer
        # _logger.info(
        #     'Running update data from visibility after update modules list')
        # cuando refresquemos desde adhoc
        # self.update_data_from_visibility()
        return res

    @api.model
    def _get_installed_uninstallable_modules(self):
        return self.search([
            ('conf_visibility', 'in', uninstallables),
            ('state', 'in', installed),
        ])

    @api.model
    def _get_not_installed_uninstallable_modules(self):
        return self.search([
            ('conf_visibility', 'in', uninstallables),
            ('state', 'in', not_installed),
        ])

    @api.model
    def _get_installed_uncontracted_modules(self):
        return self.search([
            ('adhoc_category_id', '!=', False),
            ('adhoc_category_id.contracted', '=', False),
            ('state', 'in', installed),
        ])

    @api.model
    def _get_not_installed_by_category_modules(self):
        # make none auto_install modules auto_install if vis. auto_install and
        # in categorias contratadas o que no requieren contrato
        return self.search([
            '&', ('conf_visibility', '=', 'auto_install_by_categ'),
            ('adhoc_category_id.contracted', '=', True),
            ('state', '=', 'uninstalled'),
        ])

    @api.model
    def update_data_from_visibility(self):
        # TODO mejorar performance de esto
        _logger.info('Updating data from visibility')
        self.update_uninstallable_state()
        self.update_auto_install_from_visibility()
        self.set_to_install_from_category()
        self.set_to_install_autoinstall()
        return True

    @api.model
    def set_to_install_autoinstall(self):
        """
        Marcamos para instalar todos los modulos que tengan auto install if
        categ y las categ esten contratadas
        """
        to_install_modules = self._get_not_installed_autoinstall_modules()
        to_install_modules._set_to_install()

    @api.model
    def set_to_install_from_category(self):
        """
        Marcamos para instalar todos los modulos que tengan auto install if
        categ y las categ esten contratadas
        """
        to_install_modules = self._get_not_installed_by_category_modules()
        to_install_modules._set_to_install()

    @api.model
    def update_auto_install_from_visibility(self):
        # make none auto_install modules auto_install if vis. auto_install
        visibility_auto_install_modules = self.search([
            ('conf_visibility', '=', 'auto_install'),
            ('auto_install', '=', False),
        ])
        visibility_auto_install_modules.write({'auto_install': True})

        # in case an auto_install module became normal
        # we check modules with auto_install and no visibility auto install
        visibility_none_auto_install_auto_modules = self.search([
            ('conf_visibility', '!=', 'auto_install'),
            ('auto_install', '=', True),
        ])
        visibility_none_auto_install_auto_modules_names = dict(
            [(m.name, m) for m in visibility_none_auto_install_auto_modules])
        for mod_name in modules.get_modules():
            # mod is the in database
            mod = visibility_none_auto_install_auto_modules_names.get(mod_name)
            # terp is the module on file
            terp = self.get_module_info(mod_name)
            if mod:
                # si terp dice que es no es auto_intall lo ponemos false
                if not terp.get('auto_install', False):
                    mod.auto_install = False

    @api.model
    def update_uninstallable_state(self):
        """
        Just in case module list update overwrite some of our values
        """
        # make uninstallable all not installed modules that has a none
        # istallable visibility
        self._get_not_installed_uninstallable_modules().write(
            {'state': 'uninstallable'})

        # make uninstallable all modules that are not contracted
        self.search([
            ('state', '=', 'uninstalled'),
            ('adhoc_category_id.contracted', '=', False)]).write(
                {'state': 'uninstallable'})

        # we check if some uninstallable modules has become installable
        # visibility installable, dcontracte and terp says instsallable
        uninstallable_installable_modules = self.search([
            ('conf_visibility', 'not in', uninstallables),
            ('adhoc_category_id.contracted', '=', True),
            ('state', '=', 'uninstallable'),
        ])

        uninstallable_installable_modules_names = dict(
            [(m.name, m) for m in uninstallable_installable_modules])
        for mod_name in modules.get_modules():
            # mod is the in database
            mod = uninstallable_installable_modules_names.get(mod_name)
            # terp is the module on file
            terp = self.get_module_info(mod_name)
            if mod:
                # si terp dice que es instalable lo ponemos uninstalled
                if terp.get('installable', True):
                    mod.state = 'uninstalled'

    @api.model
    def _inverse_adhoc_summary(self):
        self.adhoc_summary = self.computed_summary

    @api.depends()
    def _compute_computed_summary(self):
        for rec in self:
            rec.computed_summary = rec.adhoc_summary or rec.summary

    @api.multi
    def button_un_ignore(self):
        return self.write({'state': 'uninstalled'})

    @api.multi
    def button_ignore(self):
        return self.write({'state': 'ignored'})

    @api.model
    def _get_not_installed_autoinstall_modules(self):
        # Mark (recursively) the newly satisfied modules to also be installed

        # Select all auto-installable (but not yet installed) modules.
        # como
        #     '|',
        #     ('adhoc_category_id', '=', False),
        #     ('adhoc_category_id.contracted', '=', True)
        # no funciona tuvimos que hacer este artilugio
        contracted_modules = self.search([
            ('adhoc_category_id', '=', False)]) + self.search([
                ('adhoc_category_id.contracted', '=', True)])
        domain = [
            ('state', '=', 'uninstalled'),
            ('auto_install', '=', True),
            ('id', 'in', contracted_modules.ids),
            # '|',
            # ('adhoc_category_id', '=', False),
            # ('adhoc_category_id.contracted', '=', True)
        ]
        uninstalled_modules = self.search(domain)

        # Keep those with:
        #  - all dependencies satisfied (installed or to be installed),
        #  - at least one dependency being 'to install'

        satisfied_states = frozenset(('installed', 'to install', 'to upgrade'))

        # la diferencia respecto al siguiente es que no buscamos ninguno que
        # este en "to intall"
        # TODO faltaria chequear que las dependencias satisfechas
        # esten correctamente instaladas y contratadas tambien
        def all_depencies_satisfied(m):
            states = set(d.state for d in m.dependencies_id)
            return states.issubset(satisfied_states)
            # lo hicimos en el serach arriba
            # return states.issubset
            #     (satisfied_states) and m.adhoc_category_id.contracted

        to_install_modules = filter(
            all_depencies_satisfied, uninstalled_modules)
        to_install_ids = map(lambda m: m.id, to_install_modules)
        return self.browse(to_install_ids)

    @api.multi
    def _get_to_install_autoinstall_modules(self):
        # Mark (recursively) the newly satisfied modules to also be installed

        # Select all auto-installable (but not yet installed) modules.
        domain = [('state', '=', 'uninstalled'), ('auto_install', '=', True)]
        uninstalled_modules = self.search(domain)

        # Keep those with:
        #  - all dependencies satisfied (installed or to be installed),
        #  - at least one dependency being 'to install'

        satisfied_states = frozenset(('installed', 'to install', 'to upgrade'))

        def all_depencies_satisfied(m):
            states = set(d.state for d in m.dependencies_id)
            return states.issubset(
                satisfied_states) and ('to install' in states)

        to_install_modules = filter(
            all_depencies_satisfied, uninstalled_modules)
        to_install_ids = map(lambda m: m.id, to_install_modules)
        return self.browse(to_install_ids)

    @api.model
    def get_overall_update_state(self):
        res = super(IrModuleModule, self).get_overall_update_state()
        # solo cambiamos estado si estado es ok, es decir, nuevos estados
        # tienen menos prioridad
        installed_uninstallable = self._get_installed_uninstallable_modules()
        installed_uncontracted = self._get_installed_uncontracted_modules()
        uninstalled_auto_install = (
            self._get_not_installed_autoinstall_modules())
        new_detail = {
            'installed_uninstallable': installed_uninstallable.mapped(
                'name'),
            'installed_uncontracted': installed_uncontracted.mapped(
                'name'),
            'uninstalled_auto_install': uninstalled_auto_install.mapped(
                'name'),
        }
        res['detail'].update(new_detail)
        if res.get('state') == 'ok':
            if installed_uninstallable:
                res['state'] = 'installed_uninstallable'
            elif uninstalled_auto_install:
                res['state'] = 'uninstalled_auto_install'
            # ultime prioridad porque es el unico que no se arregla con fix
            elif installed_uncontracted:
                res['state'] = 'installed_uncontracted'
        return res

    @api.multi
    def button_set_to_install(self):
        """
        Boton que devuelve wizar di hay dependencias y si no los pone a
        instalar.
        Ademas usa el _set_to_install en vez de button_install
        """
        # self.ensure_one()
        deps = self.mapped('dependencies_id.depend_id')
        uninstalled_deps = deps.filtered(
            lambda x: x.state in ['uninstalled', 'ignored'])
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
    def button_uninstall(self):
        if self.env.uid != 1:
            raise ValidationError(_(
                'Por cuestiones de seguridad, solo admin puede desinstalar '
                'módulos'))
        return super(IrModuleModule, self).button_uninstall()

    # NOTA: a partir de aca estan todos los metodos relativos a fix de ir
    # module

    # this is the status of only one module
    update_state = fields.Selection([
        ('init_and_conf_required', 'Init and Config'),
        ('update_required', 'Update'),
        ('optional_update', 'Optional Update'),
        ('ok', 'Ok'),
    ],
        'Update Status',
        compute='_compute_update_state',
    )

    @api.depends('installed_version', 'latest_version')
    def _compute_update_state(self):
        """
        We use version number Guidelines x.y.z from
        https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md#version-numbers
        """
        for rec in self:
            update_state = 'ok'
            # installed is module avaiable version
            # latest is the module installed version
            if rec.installed_version and rec.latest_version:
                (ix, iy, iz) = rec.get_versions(rec.installed_version)
                (lx, ly, lz) = rec.get_versions(rec.latest_version)
                if ix > lx:
                    update_state = 'init_and_conf_required'
                elif ix == lx and iy > ly:
                    update_state = 'update_required'
                elif ix == lx and iy == ly and iz > lz:
                    update_state = 'optional_update'
            rec.update_state = update_state

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
    def _get_modules_state(self):
        _logger.info('Getting modules state')
        modules_availabilty = self.get_modules_availabilty()
        # unmet_deps = modules_availabilty['unmet_deps']
        unmet_deps = self.search(
            [('name', 'in', modules_availabilty['unmet_deps'])])
        not_installable = self.search(
            [('name', 'in', modules_availabilty['not_installable'])])

        installed_modules = self.search([('state', '=', 'installed')])
        # because not_installable version could be miss understud as
        # init_and_conf_required, we remove them from this list
        init_and_conf_required = installed_modules.filtered(
            lambda r: r.update_state == 'init_and_conf_required' and
            r not in not_installable)
        update_required = installed_modules.filtered(
            lambda r: r.update_state == 'update_required')
        optional_update = installed_modules.filtered(
            lambda r: r.update_state == 'optional_update')

        to_upgrade_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to upgrade')])
        to_install_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to install')])
        to_remove_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to remove')])
        return {
            'init_and_conf_required': init_and_conf_required,
            'update_required': update_required,
            'optional_update': optional_update,
            'to_upgrade_modules': to_upgrade_modules,
            'to_remove_modules': to_remove_modules,
            'to_install_modules': to_install_modules,
            'unmet_deps': unmet_deps,
            'not_installable': not_installable,
        }

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
        modules_state = self._get_modules_state()
        unmet_deps = modules_state.get('unmet_deps')
        not_installable = modules_state.get('not_installable')
        init_and_conf_required = modules_state.get('init_and_conf_required')
        update_required = modules_state.get('update_required')
        optional_update = modules_state.get('optional_update')
        to_upgrade_modules = modules_state.get('to_upgrade_modules')
        to_install_modules = modules_state.get('to_install_modules')
        to_remove_modules = modules_state.get('to_remove_modules')

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
        # if we call it remotly we can not return modules_state
        if not self._context.get('called_locally'):
            modules_state = False
        return {
            'state': update_state,
            'modules_state': modules_state,
            'detail': {
                'init_and_conf_required': init_and_conf_required.mapped(
                    'name'),
                'update_required': update_required.mapped('name'),
                'optional_update': optional_update.mapped(
                    'name'),
                'on_to_upgrade': to_upgrade_modules.mapped('name'),
                'on_to_remove': to_remove_modules.mapped('name'),
                'on_to_install': to_install_modules.mapped('name'),
                'unmet_deps': unmet_deps.mapped('name'),
                'not_installable': not_installable.mapped('name'),
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
            file_info = modules.module.load_information_from_description_file(
                module)
            if file_info and file_info['installable']:
                packages.append((module, file_info))
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
    def _set_to_install(self):
        """
        Igual que button install pero no ejecuta automaticamente (ni devuelve
        wizard)
        """
        super(IrModuleModule, self).button_install()
        return True

    @api.multi
    def _set_to_uninstall(self):
        """
        Igual que button uninstall pero no ejecuta automaticamente (ni devuelve
        wizard)
        """
        super(IrModuleModule, self).button_uninstall()
        return True

    @api.multi
    def _set_to_upgrade(self):
        """
        Igual que button upgrade pero no ejecuta automaticamente (ni devuelve
        wizard)
        Ademas sacamos el update list para que sea mas rapido
        """
        depobj = self.env['ir.module.module.dependency']
        todo = list(self)
        # self.update_list()

        i = 0
        while i < len(todo):
            mod = todo[i]
            i += 1
            if mod.state not in ('installed', 'to upgrade'):
                raise ValidationError(_(
                    "Can not upgrade module '%s'. It is not installed.") % (
                    mod.name,))
            self.check_external_dependencies(mod.name, 'to upgrade')
            deps = depobj.search([('name', '=', mod.name)])
            for dep in deps:
                if (
                        dep.module_id.state == 'installed' and
                        dep.module_id not in todo):
                    todo.append(dep.module_id)

        ids = map(lambda x: x.id, todo)
        self.browse(ids).write({'state': 'to upgrade'})

        to_install = []
        for mod in todo:
            for dep in mod.dependencies_id:
                if dep.state == 'unknown':
                    raise ValidationError(_(
                        'You try to upgrade a module that depends on the '
                        'module: %s.\nBut this module is not available in '
                        'your system.') % (dep.name,))
                if dep.state == 'uninstalled':
                    ids2 = self.search([('name', '=', dep.name)])
                    to_install.extend(ids2.ids)

        self.browse(to_install)._set_to_install()
        return True
