# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, SUPERUSER_ID, _
# from erppeek import Client
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    remote_partner_uuid = fields.Char(
        'Remote Partner UUID',
        readonly=False,
        copy=False,
    )

    @api.multi
    def action_reset_password(self):
        self.check_pass_change()
        return super(ResUsers, self).action_reset_password()

    @api.multi
    @api.constrains('password')
    def check_pass_change(self):
        for rec in self:
            if rec.id == SUPERUSER_ID and rec.env.user.id != SUPERUSER_ID:
                raise Warning(_(
                    'Only Admin can change his password'))
