# -*- coding: utf-8 -*-
from openerp import fields, models, _, api
import string


def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.
"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')
    return filename


class Doc_Toc(models.Model):
    _inherit = 'website.doc.toc'

    external_id = fields.Char(
        'External ID',
        help="Used to identify this resource when consumed by ws"
        )
    required_module_id = fields.Many2one(
        'ir.module.module',
        'Required Module',
        )
    _sql_constraints = [
        (
            'external_id_unique',
            'unique(external_id)',
            _('External ID must be unique.')
        )
    ]

    @api.one
    @api.onchange('name')
    def onchange_name(self):
        if not self.external_id and self.name:
            self.external_id = format_filename(self.name)


class Google_doc(models.Model):
    _inherit = 'website.doc.google_doc'

    required_module_id = fields.Many2one(
        'ir.module.module',
        'Required Module',
        )
    external_id = fields.Char(
        'External ID',
        help="Used to identify this resource when consumed by ws"
        )
    _sql_constraints = [
        (
            'external_id_unique',
            'unique(external_id)',
            _('External ID must be unique.')
        )
    ]

    @api.one
    @api.onchange('name')
    def onchange_name(self):
        if not self.external_id and self.name:
            self.external_id = format_filename(self.name)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
