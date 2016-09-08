# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import logging

_logger = logging.getLogger(__name__)


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    implemented = fields.Boolean(
        'Implementado',
        help='Este producto a sido implementado por nosotros y debe tener '
        'garantia'
    )

    _sql_constraints = [(
        'product_uniq',
        'unique (product_id, analytic_account_id)',
        'Product muts be unique per contract!')
    ]
