##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class module_dependency(models.Model):
    _inherit = "ir.module.module.dependency"

    state = fields.Selection(
        selection_add=[('ignored', 'Ignored')]
    )
