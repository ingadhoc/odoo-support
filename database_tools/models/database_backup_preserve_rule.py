# -*- encoding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class db_database_backup_preserve_rule(models.Model):

    _name = 'db.database.backup.preserve_rule'

    name = fields.Char(
        'Name',
        required=True,
    )
    interval = fields.Integer(
        string='Interval',
        required=True,
    )
    interval_type = fields.Selection([
        ('hourly', 'Hour(s)'),
        ('daily', 'Day(s)'),
        ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'),
        ('yearly', 'Year(s)'),
    ],
        'Type',
        required=True,
    )
    term = fields.Integer(
        string='Term',
        required=True,
    )
    term_type = fields.Selection([
        ('hourly', 'Hour(s)'),
        ('daily', 'Day(s)'),
        ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'),
        ('yearly', 'Year(s)'),
    ],
        'Type',
        required=True,
    )

    @api.one
    @api.constrains('interval', 'term')
    def check_interval_and_term(self):
        if self.interval == 0:
            raise ValidationError(_('Interval can not be 0'))
        if self.term == 0:
            raise ValidationError(_('Term can not be 0'))
