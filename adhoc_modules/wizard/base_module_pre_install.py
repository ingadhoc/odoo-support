# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, fields
# from openerp.exceptions import Warning


class BaseModulePreInstall(models.TransientModel):
    """ Module Pre Upgrade """

    _name = 'base.module.pre.install'

    module_id = fields.Many2one(
        'ir.module.module',
        string='Module',
        required=True,
        readonly=True,
    )
    dependency_ids = fields.Many2many(
        'ir.module.module',
        string='Uninstalled Dependencies',
        readonly=True,
    )

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.module_id._set_to_install()
        # esta era la alternativa usando bus, sacado de aquí
        # http://stackoverflow.com/questions/30784771/
        # reload-kanban-view-after-a-wizards-closes-in-odoo-8/32998076#32998076
        # bus = self.env['bus.bus']
        # message = {
        #     'subject': '',
        #     'body': 'Appointment Set',
        #     'mode': 'notify',
        # }
        # bus.sendone('<CHANNEL-NAME>', message)

        # return True
        # hicimos el modulo web_action_close_wizard_view_reload para
        # que se recargue automaticamente
        return {'type': 'ir.actions.act_window_close'}
        # return {'type': 'ir.actions.act_close_wizard_and_reload_view'}
