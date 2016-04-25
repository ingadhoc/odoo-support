# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import logging

_logger = logging.getLogger(__name__)


class module_dependency(models.Model):
    _inherit = "ir.module.module.dependency"

    state = fields.Selection(
        selection_add=[('ignored', 'Ignored')]
    )
