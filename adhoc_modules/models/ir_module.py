# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
# from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class AdhocModuleModule(models.Model):
    _inherit = 'ir.module.module'

    adhoc_category_id = fields.Many2one(
        'adhoc.module.category',
        'ADHOC Category',
        auto_join=True,
        )
    computed_summary = fields.Char(
        compute='get_computed_summary',
        inverse='set_adhoc_summary',
        )
    adhoc_summary = fields.Char(
        )
    adhoc_description_html = fields.Html(
        )
    support_type = fields.Selection([
        ('supported', 'Soportado'),
        ('unsupported', 'No Soportado'),
        # ('unsupport_all', 'No Soporta BD'),
        ],
        string='Support Type',
        )
    review = fields.Selection([
        ('0', 'Not Recommended'),
        ('1', 'Only If Necessary'),
        ('2', 'Neutral'),
        ('3', 'Recomendado'),
        ('4', 'Muy Recomendado'),
        ], 'Opinion',
        select=True
        )
    conf_visibility = fields.Selection([
        # instalables
        ('normal', 'Normal'),
        ('only_if_depends', 'Solo si dependencias'),
        ('auto_install', 'Auto Install'),
        ('installed_by_others', 'Instalado por Otro'),
        ('on_config_wizard', 'En asistente de configuración'),
        # no instalable
        ('to_review', 'A Revisar'),
        ('future_versions', 'Versiones Futuras'),
        ('unusable', 'No Usable'),
        ],
        'Visibility',
        required=True,
        default='normal',
        help="Módulos que se pueden instalar:\n"
        "* Normal: visible para ser instalado\n"
        "* Solo si dependencias: se muestra solo si dependencias instaladas\n"
        "* Auto Instalar: auto instalar si se cumplen dependencias\n"
        "* Instalado por Otro: algún otro módulo dispara la instalación\n"
        "* En asistente de configuración: este módulo esta presente en el "
        "asistente de configuración\n"
        "\nMódulos en los que se bloquea la instalación:\n"
        "* A Revisar: hay que analizar como lo vamos a utilizar\n"
        "* Versiones Futuras: se va a incorporar más adelante\n"
        "* No Usable: no se usa ni se va a sugerir uso en versiones futuras\n"
        )
    visibility_obs = fields.Char(
        'Visibility Observation'
        )
    ignored = fields.Boolean(
        'Ignored'
        )
    to_check = fields.Boolean(
        compute='get_to_check',
        search='search_to_check',
        string='To Check',
        )

    @api.one
    def get_to_check(self):
        to_check = True
        if self.ignored:
            to_check = False
        elif (self.conf_visibility == 'only_if_depends' and not self.depends):
            to_check = False
        elif self.conf_visibility != 'normal':
            to_check = False
        self.to_check = to_check

    @api.model
    def search_to_check(self, operator, value):
        # if operator 
        # normal_modules = self.search([
        #     ('ignored', '!=', True),
        #     ('conf_visibility', '=', 'normal'),
        #     # ('depends.dependencies_id', '=', 'only_if_depends'),
        #     ])
        # only_if_depends_modules = self.search([
        #     ('ignored', '!=', True),
        #     ('conf_visibility', '=', 'only_if_depends'),
        #     ('dependencies_id.depend_id.state', '=', 'installed'),
        #     ])
        return [
            ('ignored', '!=', True),
            ('conf_visibility', '=', 'normal'),
            '|', ('conf_visibility', '=', 'only_if_depends'),
            ('dependencies_id.depend_id.state', '=', 'installed'),
            ]
            # ('conf_visibility', '=', 'only_if_depends'),
        # self.search(['conf_'])

    @api.model
    def set_adhoc_summary(self):
        self.adhoc_summary = self.computed_summary

    @api.one
    def get_computed_summary(self):
        self.computed_summary = self.adhoc_summary or self.summary

    @api.multi
    def open_module(self):
        self.ensure_one()
        module_form = self.env.ref(
            'adhoc_modules.view_adhoc_module_module_form', False)
        if not module_form:
            return False
        return {
            'name': _('Module Description'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._model,
            'views': [(module_form.id, 'form')],
            'view_id': module_form.id,
            'res_id': self.id,
            'target': 'current',
            # 'target': 'new',
            'context': self._context,
            # top open in editable form
            'flags': {
                'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
            }

    @api.multi
    def button_ignore(self):
        return self.write({'ignored': True})

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
