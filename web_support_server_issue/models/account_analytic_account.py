# -*- coding: utf-8 -*-
from openerp import models, api, _


class Contract(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def create_issue(self, db_name, remote_user_id, vals):
        self.ensure_one()
        database = self.env['infrastructure.database'].sudo().search([
            ('name', '=', db_name), ('contract_id', '=', self.id)], limit=1)
        if not database:
            return {'error': _("No database found")}
        vals['database_id'] = database.id

        project = self.env['project.project'].sudo().search(
            [('analytic_account_id', '=', self.id)], limit=1)
        if project:
            vals['project_id'] = project.id

        # TODO agregar el campo contract a los issues y habilitar esto
        issue = self.env['project.issue'].sudo().create(vals)
        return {'issue_id': issue.id}
