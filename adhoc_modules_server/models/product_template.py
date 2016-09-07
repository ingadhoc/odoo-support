# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import logging

_logger = logging.getLogger(__name__)


class ProductTempalte(models.Model):
    _inherit = 'product.template'

    adhoc_category_ids = fields.Many2many(
        'adhoc.module.category.server',
        'adhoc_module_category_product_rel',
        'product_tmpl_id', 'adhoca_category_id',
        string='Categories',
    )
    adhoc_product_dependency_ids = fields.Many2many(
        'product.template',
        'product_adhoc_depedency_rel',
        'product_tmpl_id', 'product_tmpl_dependency_id',
        string='Dependencies',
    )
