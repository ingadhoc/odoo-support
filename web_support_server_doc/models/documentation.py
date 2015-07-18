# -*- coding: utf-8 -*-
from openerp import fields, models


# def format_filename(s):
#     """Take a string and return a valid filename constructed from the string.
# Uses a whitelist approach: any characters not present in valid_chars are
# removed. Also spaces are replaced with underscores.

# Note: this method may produce invalid filenames such as ``, `.` or `..`
# When I use this method I prepend a date string like '2009_01_15_19_46_32_'
# and append a file extension like '.txt', so I avoid the potential of using
# an invalid filename.
# """
#     valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
#     filename = ''.join(c for c in s if c in valid_chars)
#     filename = filename.replace(' ', '_')
#     return filename.lower()


class Documentation(models.Model):
    _inherit = 'website.doc.toc'

    state = fields.Selection(
        [('private', 'Is Private'),
         ('published', 'Published')],
        'State',
        required=True,
        default='published',
        # default='private',
        help="If private, then it wont be accesible by portal or public users"
        )
    required_module_id = fields.Many2one(
        'ir.module.module',
        'Required Module',
        )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        help='If partner is set, only this partner will be able\
        to download this item',
        )
    # external_ref = fields.Char(
    #     'External ID Ref',
    #     )

    # @api.one
    # @api.onchange('name')
    # def change_name(self):
    #     if not self.external_ref and self.name:
    #         self.external_ref = format_filename(self.name)

    # @api.one
    # @api.constrains('state')
    # def check_state(self):
    #     if self.state == 'published' and not self.external_ref:
    #         raise Warning(
    #             _('To publish you must first set an External ID Ref'))

    # @api.one
    # def unlink(self):
    #     ir_model_data = self.sudo().env['ir.model.data']
    #     actual_model_data = ir_model_data.search([
    #         ('module', '=', 'web_support_server_doc'),
    #         ('res_id', '=', self.id),
    #         ('model', '=', self._name),
    #         ], limit=1)
    #     actual_model_data.unlink()
    #     return super(Documentation, self).unlink()

    # @api.one
    # @api.constrains('external_ref')
    # def create_external_id(self):
    #     if self.external_ref:
    #         ir_model_data = self.sudo().env['ir.model.data']
    #         actual_model_data = ir_model_data.search([
    #             ('module', '=', 'web_support_server_doc'),
    #             ('res_id', '=', self.id),
    #             ('model', '=', self._name),
    #             ], limit=1)
    #         if actual_model_data:
    #             actual_model_data.name = self.external_ref
    #         else:
    #             ir_model_data.create({
    #                 'model': self._name,
    #                 'res_id': self.id,
    #                 'module': 'web_support_server_doc',
    #                 'name': self.external_ref,
    #             })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
