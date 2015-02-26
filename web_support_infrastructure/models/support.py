# -*- coding: utf-8 -*-
from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class Database(models.Model):
    _inherit = 'infrastructure.database'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
