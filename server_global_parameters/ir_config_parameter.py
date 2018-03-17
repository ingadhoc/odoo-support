from odoo import models, api
import odoo.tools as tools


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
