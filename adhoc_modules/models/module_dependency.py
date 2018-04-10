##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ModuleDependency(models.Model):
    _inherit = "ir.module.module.dependency"

    state = fields.Selection(
        selection_add=[('ignored', 'Ignored')]
    )
