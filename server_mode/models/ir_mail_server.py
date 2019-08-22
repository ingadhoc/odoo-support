from odoo import models, api, _
from odoo.addons.server_mode.mode import get_mode
import logging
_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def send_email(
            self, message, mail_server_id=None, smtp_server=None,
            smtp_port=None, smtp_user=None, smtp_password=None,
            smtp_encryption=None, smtp_debug=False, smtp_session=None):
        # TODO
        # if we raise ValidationError then can not install modules with demo
        # data, we should find a way to raise message when sending from
        # interface
        # raise ValidationError(_(
        if get_mode():
            _logger.log(25, _(
                "You Can not Send Mail Because Odoo is not in Production "
                "mode"))
            return True
        return super(IrMailServer, self).send_email(
            message, mail_server_id=mail_server_id,
            smtp_server=smtp_server, smtp_port=smtp_port,
            smtp_user=smtp_user, smtp_password=smtp_password,
            smtp_encryption=smtp_encryption, smtp_debug=smtp_debug,
            smtp_session=smtp_session)
