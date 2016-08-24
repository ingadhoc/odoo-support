# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models
# from erppeek import Client
# from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    remote_partner_uuid = fields.Char(
        'Remote Partner UUID',
        readonly=False,
    )
