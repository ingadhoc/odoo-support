# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, fields, _
from openerp.exceptions import Warning


class BaseModulePreUpgrade(models.TransientModel):
    """ Module Pre Upgrade """

    _inherit = 'base.module.upgrade'

    recent_backup = fields.Boolean(
        readonly=True,
    )
    low_review_module_ids = fields.Many2many(
        'ir.module.module',
        compute='get_low_review_modules',
        string='Low Review Modules',
    )

    @api.one
    @api.depends('module_info')
    def get_low_review_modules(self):
        low_review_modules = self.env['ir.module.module'].search([
            ('state', '=', 'to install'),
            ('review', 'in', ['0', '1']),
        ])
        self.low_review_module_ids = low_review_modules

    @api.multi
    def backup_now(self):
        db = self.env['db.database'].search([('type', '=', 'self')], limit=1)
        if not db:
            raise Warning(_(
                'No Database "Self" found on Database Tools Databses'))
        db.database_backup()
        self.recent_backup = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def upgrade_module(self):
        super(BaseModulePreUpgrade, self).upgrade_module()
        # retornamos reload en vez de solo cerrar ventana
        # reload the client; open the first available root menu
        menu = self.env['ir.ui.menu'].search(
            [('parent_id', '=', False)], limit=1)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id}
        }
