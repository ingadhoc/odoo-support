# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
# from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class module_dependency(models.Model):
    _inherit = "ir.module.module.dependency"

    state = fields.Selection(
        selection_add=[('ignored', 'Ignored')]
        )
    # state = fields.Selection(DEP_STATES, string='Status', compute='_compute_state')
    # depend_id = fields.Many2one(search='search_depend_id')

    # @api.model
    # def search_depend_id(self):
    #     return
