# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, fields
from openerp.tools.parse_version import parse_version
import logging
_logger = logging.getLogger(__name__)


class ir_module_module(models.Model):
    _inherit = "ir.module.module"

    update_state = fields.Selection([
        ('init_and_conf', 'To Init and Config'),
        ('update', 'To Update'),
        ('optional_update', 'Optional Updaet'),
        ('ok', 'Ok'),   # ok if not installed or up to date
        ],
        'Update Status',
        readonly=True,
        compute='get_update_state',
        # store=True,
        )

    @api.one
    @api.depends('installed_version', 'latest_version')
    def get_update_state(self):
        """
        We use version number Guidelines x.y.z from
        https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md#version-numbers
        """
        update_state = 'ok'
        if self.installed_version and self.latest_version:
            (ix, iy, iz) = self.get_versions(self.installed_version)
            (lx, ly, lz) = self.get_versions(self.latest_version)
            if ix > lx:
                update_state = 'init_and_conf'
            elif iy > ly:
                update_state = 'update'
            elif iz > lz:
                update_state = 'optional_update'
        self.update_state = update_state

    @api.model
    def get_versions(self, version):
        # we take out mayor version
        parsed = list(parse_version(version)[2:])
        x = parsed and parsed.pop(0) or False
        y = parsed and parsed.pop(0) or False
        z = parsed and parsed.pop(0) or False
        return (x, y, z)
