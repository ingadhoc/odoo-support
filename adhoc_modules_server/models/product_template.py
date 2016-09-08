# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductTempalte(models.Model):
    _inherit = 'product.template'

    adhoc_category_ids = fields.Many2many(
        'adhoc.module.category.server',
        'adhoc_module_category_product_rel',
        'product_tmpl_id', 'adhoca_category_id',
        string='Categories',
    )
    # TODO en realidad esta dependencia deberia ser en clase product
    # product
    adhoc_product_dependency_ids = fields.Many2many(
        'product.template',
        'product_adhoc_depedency_rel',
        'product_tmpl_id', 'product_tmpl_dependency_id',
        string='Dependencies',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    contract_state = fields.Selection([
        ('contracted', 'contracted'), ('un_contracted', 'un_contracted')
    ],
        'Contract State',
        compute='_compute_contract_state',
    )

    @api.multi
    def _compute_contract_state(self):
        contract = self._get_contract()
        if not contract:
            return False
        for product in self:
            # we use filtered instead of compute because of cache
            lines = contract.recurring_invoice_line_ids.filtered(
                lambda x: x.product_id == product)
            if lines:
                product.contract_state = 'contracted'
            else:
                product.contract_state = 'un_contracted'

    @api.multi
    def _add_to_contract(self, contract):
        contract_line = self.env['account.analytic.invoice.line']
        partner = contract.partner_id
        pricelist = contract.pricelist_id
        quantity = 1.0
        for product in self:
            line = contract_line.search([
                ('analytic_account_id', '=', contract.id),
                ('product_id', '=', product.id)], limit=1)
            # just in case quantity is zero
            if line:
                line.quantity = 1.0
            else:
                res = contract_line.product_id_change(
                    product.id, False, qty=quantity,
                    name=False, partner_id=partner.id, price_unit=False,
                    pricelist_id=pricelist.id, company_id=None).get(
                    'value', {})
                vals = {
                    'analytic_account_id': contract.id,
                    'product_id': product.id,
                    'quantity': quantity,
                    'name': res.get('name'),
                    'uom_id': res.get('uom_id'),
                    'price_unit': res.get('price_unit'),
                    'tax_id': res.get('tax_id'),
                }
                contract_line.create(vals)
            dep_prods = product.adhoc_product_dependency_ids.mapped(
                'product_variant_ids')
            dep_prods._add_to_contract(contract)

    @api.multi
    def _remove_from_contract(self, contract):
        contract_line = self.env['account.analytic.invoice.line']
        for product in self:
            contract_line.search([
                ('analytic_account_id', '=', contract.id),
                ('product_id', '=', product.id)]).unlink()
            upper_prods = self.search([(
                'adhoc_product_dependency_ids',
                '=',
                product.product_tmpl_id.id)])
            upper_prods._remove_from_contract(contract)

    @api.model
    def _get_contract(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        contract_id = self._context.get('active_id', False)
        if not active_id or active_model != 'account.analytic.account':
            return False
        return self.env[active_model].browse(contract_id)

    @api.multi
    def action_add_to_contract(self):
        contract = self._get_contract()
        self._add_to_contract(contract)

    @api.multi
    def action_remove_to_contract(self):
        contract = self._get_contract()
        self._remove_from_contract(contract)
