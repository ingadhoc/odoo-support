# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
import string
_logger = logging.getLogger(__name__)


class AdhocModuleCategory(models.Model):
    _name = 'adhoc.module.category'
    # we add parent order so we can fetch in right order to upload data
    # correctly
    _order = 'sequence'
    # _order = "parent_left"
    _parent_store = True
    _parent_order = "sequence"
    # _rec_name = 'display_name'

    visibility = fields.Selection([
        ('normal', 'Normal'),
        ('product_required', 'Product Required'),
    ],
        required=True,
        readonly=True,
        default='normal',
    )
    contracted_product = fields.Char(
        readonly=True,
    )
    name = fields.Char(
        readonly=True,
        required=True,
    )
    code = fields.Char(
        readonly=True,
        # required=True,
        # readonly=True,
        # default='/',
    )
    count_modules = fields.Integer(
        string='# Modules',
        compute='get_count_modules',
    )
    count_pending_modules = fields.Integer(
        string='# Revised Modules',
        compute='get_count_modules',
    )
    count_revised_modules = fields.Integer(
        string='# Revised Modules',
        compute='get_count_modules',
    )
    # count_subcategories_modules = fields.Integer(
    # string='# Subcategories Modules',
    #     compute='get_count_subcategories_modules',
    #     )
    # count_suggested_subcategories_modules = fields.Integer(
    # string='# Suggested Subcategories Modules',
    #     compute='get_count_subcategories_modules',
    #     )
    count_subcategories = fields.Integer(
        string='# Subcategories',
        compute='get_count_subcategories',
    )
    count_revised_subcategories = fields.Integer(
        string='# Revised Subcategories',
        compute='get_count_subcategories',
    )
    color = fields.Integer(
        string='Color Index',
        compute='get_color',
    )
    parent_id = fields.Many2one(
        'adhoc.module.category',
        'Parent Category',
        select=True,
        ondelete='restrict',
        readonly=True,
    )
    parent_left = fields.Integer(
        'Parent Left',
        select=1
    )
    parent_right = fields.Integer(
        'Parent Right',
        select=1
    )
    child_ids = fields.One2many(
        'adhoc.module.category',
        'parent_id',
        'Child Categories',
        readonly=True,
    )
    module_ids = fields.One2many(
        'ir.module.module',
        'adhoc_category_id',
        'Modules',
        domain=[('visible', '=', True)],
        readonly=True,
    )
    description = fields.Text(
        readonly=True,
    )
    sequence = fields.Integer(
        'Sequence',
        default=10,
        readonly=True,
    )
    to_revise = fields.Boolean(
        compute='get_to_revise',
        search='search_to_revise',
    )
    display_name = fields.Char(
        compute='get_display_name',
        # store=True
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
            'Category name must be unique'),
    ]

    @api.one
    @api.depends()
    def get_to_revise(self):
        if 'uninstalled' in self.module_ids.mapped('state'):
            self.to_revise = True
        elif True in self.child_ids.mapped('to_revise'):
            self.to_revise = True
        else:
            self.to_revise = False

    @api.model
    def search_to_revise(self, operator, value):
        """Se tiene que revisar si hay modulos o categorías a revisar"""
        # TODO mejorar, en teoria esta soportando solo dos niveles de
        # anidamiento con esta form
        # intente child_ids.to_revise = True pero dio max recursion
        # una alternativa es buscar todos los modulos uninstalled y visible
        # agruparlos por categoria y buscar las categorías padres de esas
        return [
            '|', ('module_ids.state', 'in', ['uninstalled']),
            ('child_ids.module_ids.state', 'in', ['uninstalled']),
        ]

    @api.one
    @api.constrains('child_ids', 'name', 'parent_id')
    def set_code(self):
        # if not self.code:
        code = self.display_name
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        code = ''.join(c for c in code if c in valid_chars)
        code = code.replace(' ', '').replace('.', '').lower()
        self.code = code

    @api.multi
    @api.depends('child_ids', 'name', 'parent_id')
    def get_display_name(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res
        for cat in self:
            cat.display_name = " / ".join(reversed(get_names(cat)))

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.display_name))
        return result

    @api.one
    @api.depends('child_ids')
    def get_count_subcategories(self):
        self.count_subcategories = len(self.child_ids)
        self.count_revised_subcategories = len(self.child_ids.filtered(
            lambda x: not x.to_revise))

    @api.multi
    def get_subcategories_modules(self):
        self.ensure_one()
        return self.module_ids.search([
            ('adhoc_category_id', 'child_of', self.id)])

    @api.multi
    def get_suggested_subcategories_modules(self):
        self.ensure_one()
        return self.module_ids.search([
            ('adhoc_category_id', 'child_of', self.id),
            ('state', '=', 'uninstalled'),
        ])

    # @api.model
    # def search_count_subcategories_modules(self, operator, value):
    #     sub_modules = self.get_suggested_subcategories_modules()
    #     if operator == 'like':
    #         operator = 'ilike'
    #     return [('name', operator, value)]

    # @api.one
    # def get_count_subcategories_modules(self):
    #     self.count_suggested_subcategories_modules = len(
    #         self.get_suggested_subcategories_modules())
    #     self.count_subcategories_modules = len(
    #         self.get_subcategories_modules())

    @api.one
    @api.depends('module_ids')
    def get_count_modules(self):
        count_modules = len(self.module_ids)
        count_pending_modules = len(self.module_ids.filtered(
            lambda x: x.state == 'uninstalled'))
        self.count_modules = count_modules
        self.count_pending_modules = count_pending_modules
        self.count_revised_modules = count_modules - count_pending_modules

    # @api.depends('state')
    @api.one
    def get_color(self):
        color = 4
        # TODO implementar color de las no contratadas
        # if self.count_pending_modules:
        if self.visibility != 'normal' and not self.contracted_product:
            color = 1
        elif self.to_revise:
            color = 7
        # elif self.state == 'cancel':
        #     color = 1
        # elif self.state == 'inactive':
        #     color = 3
        # if self.overall_state != 'ok':
        #     color = 2
        self.color = color

    @api.multi
    def action_subcategories(self):
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'adhoc_modules.action_adhoc_module_category')

        if not action:
            return False
        res = action.read()[0]
        res['context'] = {
            'search_default_parent_id': self.id,
            'search_default_to_revise': 1,
            'search_default_not_contracted': 1
        }
        return res

    @api.multi
    def action_modules(self):
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'adhoc_modules.action_adhoc_ir_module_module')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('adhoc_category_id', '=', self.id)]
        res['context'] = {
            # 'search_default_not_ignored': 1,
            'search_default_state': 'uninstalled',
        }
        return res

    # @api.multi
    # def action_subcategories_modules(self):
    #     self.ensure_one()
    #     action = self.env['ir.model.data'].xmlid_to_object(
    #         'adhoc_modules.action_adhoc_ir_module_module')

    #     if not action:
    #         return False
    #     res = action.read()[0]
    #     modules = self.get_subcategories_modules()
    #     res['domain'] = [('id', 'in', modules.ids)]
    #     res['context'] = {
    # 'search_default_not_ignored': 1,
    #         'search_default_state': 'uninstalled',
    #         'search_default_group_by_adhoc_category': 1
    #         }
    #     return res
