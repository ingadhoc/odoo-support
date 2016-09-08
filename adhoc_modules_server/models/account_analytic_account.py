# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
# from openerp.exceptions import Warning


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    product_ids = fields.One2many(
        'product.product',
        # 'product.template',
        string='Products',
        compute='_compute_products',
    )
    product_categ_id = fields.Many2one(
        'product.category',
        'Modules Category',
    )

    @api.multi
    def select_contract_products(self):
        self.ensure_one()
        view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'adhoc_modules_server.product_product_kanban_view')
        return {
            'name': _('Products'),
            'view_type': 'form',
            "view_mode": 'kanban',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.product_ids.ids)],
            'view_id': view_id,
        }

    @api.multi
    @api.depends('product_categ_id')
    def _compute_products(self):
        for contract in self:
            if contract.product_categ_id:
                contract.product_ids = self.env[
                    'product.product'].search([
                        ('categ_id', '=', contract.product_categ_id.id)])
