# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class database_user(models.Model):
    _inherit = "infrastructure.database.user"

    authorized_for_issues = fields.Boolean(
        'Authorized For Issues?'
        )
