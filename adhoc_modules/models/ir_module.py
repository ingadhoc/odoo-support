# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)
uninstallables = ['to_review', 'future_versions', 'unusable']


class AdhocModuleModule(models.Model):
    _inherit = 'ir.module.module'

    adhoc_category_id = fields.Many2one(
        'adhoc.module.category',
        'ADHOC Category',
        auto_join=True,
        readonly=True,
    )
    computed_summary = fields.Char(
        compute='get_computed_summary',
        inverse='set_adhoc_summary',
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
    )
    review = fields.Selection([
        ('0', 'Not Recommended'),
        ('1', 'Only If Necessary'),
        ('2', 'Neutral'),
        ('3', 'Recomendado'),
        ('4', 'Muy Recomendado'),
    ], 'Opinion',
        select=True,
        readonly=True,
    )
    conf_visibility = fields.Selection([
        # instalables
        ('normal', 'Normal'),
        ('only_if_depends', 'Solo si dependencias'),
        ('auto_install', 'Auto Install'),
        # los auto install por defecto los estamos filtrando y no categorizando
        # ('auto_install_by_module', 'Auto Install by Module'),
        ('installed_by_others', 'Instalado por Otro'),
        ('on_config_wizard', 'En asistente de configuración'),
        # no instalable
        ('to_review', 'A Revisar'),
        ('future_versions', 'Versiones Futuras'),
        ('unusable', 'No Usable'),
    ],
        'Visibility',
        required=True,
        readonly=True,
        default='normal',
        help="Módulos que se pueden instalar:\n"
        "* Normal: visible para ser instalado\n"
        "* Solo si dependencias: se muestra solo si dependencias instaladas\n"
        "* Auto Instalar: auto instalar si se cumplen dependencias\n"
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
    visible = fields.Boolean(
        compute='get_visible',
        search='search_visible',
    )
    state = fields.Selection(
        selection_add=[('ignored', 'Ignored')]
    )

    @api.one
    @api.constrains('state')
    def check_module_is_installable(self):
        if (
                self.state == 'to install' and
                self.conf_visibility in uninstallables):
            raise Warning(_(
                'You can not install module %s as is %s') % (
                self.name, self.conf_visibility))

    @api.one
    @api.depends('adhoc_category_id', 'conf_visibility')
    def get_visible(self):
        visible = True
        # si esta en estos estados, no importa el resto, queremos verlo
        if self.state in ['installed', 'to install']:
            visible = True
        elif not self.adhoc_category_id:
            visible = False
        elif (
                self.adhoc_category_id.visibility == 'product_required' and
                not self.adhoc_category_id.contracted_product
        ):
            visible = False
        elif self.conf_visibility == 'only_if_depends':
            uninstalled_dependencies = self.dependencies_id.mapped(
                'depend_id').filtered(
                lambda x: x.state not in ['installed', 'to install'])
            if uninstalled_dependencies:
                visible = False
        elif self.conf_visibility != 'normal':
            visible = False
        self.visible = visible

    @api.model
    def search_visible(self, operator, value):
        installed_modules_names = self.search([
            ('state', 'in', ['installed', 'to install'])]).mapped('name')
        return [
            '|', ('state', 'in', ['installed', 'to install']),
            '&', ('adhoc_category_id', '!=', False),
            '&', '|', ('adhoc_category_id.visibility', '=', 'normal'),
            '&', ('adhoc_category_id.visibility', '=', 'product_required'),
            ('adhoc_category_id.contracted_product', '!=', False),
            '|', ('conf_visibility', '=', 'normal'),
            '&', ('conf_visibility', '=', 'only_if_depends'),
            # puede llegar a ser necesario si no tiene dependencias pero
            # no tendria sentido
            # '|', ('dependencies_id', '=', False),
            ('dependencies_id.name', 'in', installed_modules_names),
        ]

    @api.model
    def set_adhoc_summary(self):
        self.adhoc_summary = self.computed_summary

    @api.one
    def get_computed_summary(self):
        self.computed_summary = self.adhoc_summary or self.summary

    @api.multi
    def button_un_ignore(self):
        return self.write({'state': 'uninstalled'})

    @api.multi
    def button_ignore(self):
        return self.write({'state': 'ignored'})
        # return self.write({'ignored': True})

    @api.multi
    def button_set_to_install(self):
        """
        Casi igual a "button_install" pero no devuelve ninguna acción, queda
        seteado unicamente
        """
        # Mark the given modules to be installed.
        self.state_update('to install', ['uninstalled'])

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

        # Mark them to be installed.
        if to_install_ids:
            self.browse(to_install_ids).button_install()

        return True
