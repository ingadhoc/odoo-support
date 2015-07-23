# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api, models, _
from openerp.addons.base.res.res_request import referencable_models


class support_new_issue_wizzard(models.TransientModel):
    _name = "support.new_issue.wizard"
    _description = "Support - New Issue Wizard"

    user_id = fields.Many2one(
        'res.users',
        required=True,
        default=lambda self: self.env.user,
        )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        )
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now
        )
    name = fields.Char(
        string='Title',
        required=True,
        )
    description = fields.Html(
        string='Description',
        required=True,
        )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'new_issue_ir_attachments_rel'
        'wizard_id', 'attachment_id',
        string='Attachments',
        required=False,
        )
    resource = fields.Reference(
        selection=lambda self: referencable_models(
            self, self.env.cr, self.env.uid, self.env.context),
        string='Resource',
        help='You can reference the model and record related to the issue,\
        this will help our technicians to resolve the issue faster',
        required=False,
        )
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High')],
        'Priority',
        )

    @api.onchange('user_id')
    def change_user(self):
        self.company_id = self.user_id.company_id.id

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        active_contract = self.env['support.contract'].get_active_contract()
        description = self.description
        if self.resource:
            description += '\nResource: %s' % str(self.resource)
        vals = {
            'db_user': self.user_id.login,
            'db_company': self.company_id.name,
            'date': self.date,
            'issue_description': description,
            'name': self.name,
            'priority': self.priority,
        }
        issue_id = active_contract.create_issue(vals, self.attachment_ids)
        return self.env['warning_box'].info(
            title=_('Issue succesfully loaded'),
            message=_('For your reference and if you contact support by another\
                channel, issue ID: %s') % (issue_id))
