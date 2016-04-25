# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
# from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class AdhocModuleModule(models.Model):
    _inherit = 'ir.module.module'
    _name = 'adhoc.module.module'

    adhoc_category_id = fields.Many2one(
        'adhoc.module.category.server',
        'ADHOC Category',
        auto_join=True,
        readonly=False,
    )
    repository_id = fields.Many2one(
        'adhoc.module.repository',
        'Repository',
        ondelete='cascade',
        required=True,
        auto_join=True,
        readonly=True,
    )
    dependencies_id = fields.One2many(
        'adhoc.module.dependency',
        'module_id',
        'Dependencies',
        readonly=True,
    )
    computed_summary = fields.Char(
        readonly=False,
    )
    adhoc_summary = fields.Char(
        readonly=False,
    )
    adhoc_description_html = fields.Html(
        readonly=False,
    )
    support_type = fields.Selection(
        readonly=False,
    )
    review = fields.Selection(
        readonly=False,
    )
    conf_visibility = fields.Selection(
        readonly=False,
    )
    visibility_obs = fields.Char(
        readonly=False,
    )

    @api.model
    def create(self, vals):
        # ir module modifies create, we need default one
        create_original = models.BaseModel.create
        module = create_original(self, vals)
        module_metadata = {
            'name': 'module_%s_%s' % (
                vals['name'],
                module.repository_id.branch.replace('.', '_')),
            'model': self._name,
            'module': 'adhoc_module_server',
            'res_id': module.id,
            'noupdate': True,
        }
        self.env['ir.model.data'].create(module_metadata)
        return module

    @api.multi
    def _update_dependencies(self, depends=None):
        self.ensure_one()
        if depends is None:
            depends = []
        existing = set(x.name for x in self.dependencies_id)
        needed = set(depends)
        for dep in (needed - existing):
            self._cr.execute(
                'INSERT INTO adhoc_module_dependency (module_id, name) '
                'values (%s, %s)', (self.id, dep))
        for dep in (existing - needed):
            self._cr.execute(
                'DELETE FROM adhoc_module_dependency WHERE module_id = %s '
                'and name = %s', (self.id, dep))
        self.invalidate_cache(['dependencies_id'])

    @api.multi
    def open_module(self):
        self.ensure_one()
        module_form = self.env.ref(
            'adhoc_modules_server.view_adhoc_module_module_form', False)
        if not module_form:
            return False
        return {
            'name': _('Module Description'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'adhoc.module.module',
            'views': [(module_form.id, 'form')],
            'view_id': module_form.id,
            'res_id': self.id,
            'target': 'current',
            'target': 'new',
            'context': self._context,
            # top open in editable form
            'flags': {
                'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }
