# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AdhocModuleCategory(models.Model):
    _name = 'adhoc.module.category'
    # _parent_store = True
    _order = 'sequence'
    # _rec_name = 'display_name'

    name = fields.Char(
        required=True,
        )
    count_modules = fields.Integer(
        string='# Modules',
        compute='get_count_modules',
        )
    count_suggested_modules = fields.Integer(
        string='# Suggested Modules',
        compute='get_count_modules',
        )
    count_subcategories_modules = fields.Integer(
        string='# Subcategories Modules',
        compute='get_count_subcategories_modules',
        )
    count_suggested_subcategories_modules = fields.Integer(
        string='# Suggested Subcategories Modules',
        compute='get_count_subcategories_modules',
        )
    count_subcategories = fields.Integer(
        string='# Subcategories',
        compute='get_count_subcategories',
        )
    count_suggested_subcategories = fields.Integer(
        string='# Suggested Subcategories',
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
        )
    child_ids = fields.One2many(
        'adhoc.module.category',
        'parent_id',
        'Child Categories'
        )
    module_ids = fields.One2many(
        'ir.module.module',
        'adhoc_category_id',
        'Modules'
        )
    description = fields.Text(
        )
    sequence = fields.Integer(
        'Sequence',
        default=10,
        )
    display_name = fields.Char(
        compute='get_display_name'
        )

    @api.multi
    @api.depends('child_ids')
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
        self.count_suggested_subcategories = len(self.child_ids.filtered(
            lambda x: x.count_suggested_subcategories_modules))

    @api.multi
    def get_subcategories_modules(self):
        self.ensure_one()
        return self.env['adhoc.module.module'].search([
            ('adhoc_category_id', 'child_of', self.id)])

    @api.multi
    def get_suggested_subcategories_modules(self):
        self.ensure_one()
        return self.env['adhoc.module.module'].search([
            ('adhoc_category_id', 'child_of', self.id),
            ('ignored', '=', False),
            ('state', '=', 'uninstalled'),
            ])

    # @api.model
    # def search_count_subcategories_modules(self, operator, value):
    #     sub_modules = self.get_suggested_subcategories_modules()
    #     if operator == 'like':
    #         operator = 'ilike'
    #     return [('name', operator, value)]

    @api.one
    def get_count_subcategories_modules(self):
        self.count_suggested_subcategories_modules = len(
            self.get_suggested_subcategories_modules())
        self.count_subcategories_modules = len(
            self.get_subcategories_modules())

    @api.one
    @api.depends('module_ids')
    def get_count_modules(self):
        self.count_modules = len(self.module_ids)
        self.count_suggested_modules = len(self.module_ids.filtered(
            lambda x: x.state != 'uninstalled' and not x.ignored))

    # @api.depends('state')
    @api.one
    def get_color(self):
        color = 4
        # if self.state == 'draft':
        #     color = 7
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
            }
        return res

    @api.multi
    def action_modules(self):
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'adhoc_modules.action_adhoc_module_module')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('adhoc_category_id', '=', self.id)]
        res['context'] = {
            'search_default_not_ignored': 1,
            'search_default_state': 'uninstalled',
            }
        return res

    @api.multi
    def action_subcategories_modules(self):
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'adhoc_modules.action_adhoc_module_module')

        if not action:
            return False
        res = action.read()[0]
        modules = self.get_subcategories_modules()
        res['domain'] = [('id', 'in', modules.ids)]
        res['context'] = {
            'search_default_not_ignored': 1,
            'search_default_state': 'uninstalled',
            'search_default_group_by_adhoc_category': 1
            }
        return res
