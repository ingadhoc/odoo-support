from odoo import models, api
import odoo.tools as tools
import logging
_logger = logging.getLogger(__name__)


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_param(self, key, default=False):
        res = super(IrConfigParameter, self).get_param(key, default=default)
        if not res:
            server_value = tools.config.get(key)
            if server_value:
                return str(server_value)
        return res

    @api.model
    def set_param(self, key, value):
        server_value = tools.config.get(key)
        if server_value == value:
            _logger.info(
                'Skping setting parameter on db because it has the same value '
                'as in the config')
            # set value = False to delete actual key
            value = False
        return super().set_param(key, value)
