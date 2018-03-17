from odoo import api, models
from ..mode import get_mode


class WebEnvironmentRibbonBackend(models.AbstractModel):

    _inherit = 'web.environment.ribbon.backend'

    @api.model
    def _prepare_ribbon_name(self):
        """ Overwrite ribbon functionality to use server_mode as the ribbon
        name instead the ir_config_parameter defineed in ribbon.name
        """
        mode = get_mode()
        return mode.upper() if mode else False
