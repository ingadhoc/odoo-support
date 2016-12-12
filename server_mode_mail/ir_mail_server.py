# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models
from openerp.addons.server_mode.mode import get_mode
import logging
_logger = logging.getLogger(__name__)


class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    def send_email(
            self, cr, uid, message, mail_server_id=None, smtp_server=None,
            smtp_port=None, smtp_user=None, smtp_password=None,
            smtp_encryption=None, smtp_debug=False, context=None):
        # TODO
        # if we raise ValidationError then can not install modules with demo
        # data, we should find a way to raise message when sending from
        # interface
        # raise ValidationError(_(
        if get_mode():
            _logger.warning(_(
                "You Can not Send Mail Because Odoo is not in Production "
                "mode"))
            return True
        return super(ir_mail_server, self).send_email(
            cr, uid, message, mail_server_id=mail_server_id,
            smtp_server=smtp_server, smtp_port=smtp_port,
            smtp_user=smtp_user, smtp_password=smtp_password,
            smtp_encryption=smtp_encryption, smtp_debug=smtp_debug,
            context=None)
