# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class db_database_backup_now_wizard(models.TransientModel):
    _name = 'db.database.backup_now.wizard'

    @api.model
    def get_default_keep_till_date(self):
        return date.strftime(date.today() + relativedelta(days=30), '%Y-%m-%d')

    backup_format = fields.Selection([
        ('zip', 'zip (With Filestore)'),
        ('pg_dump', 'pg_dump (Without Filestore)')],
        'Backup Format',
        default='zip',
        required=True,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    keep_till_date = fields.Date(
        'Keep Till Date',
        help="Only for manual backups, if not date is configured then backup "
        "won't be deleted.",
        default=get_default_keep_till_date,
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id', False)
        if not active_id:
            raise ValidationError(
                _("Can not run backup now, no active_id on context"))
        database = self.env['db.database'].browse(active_id)
        name = "%s.%s" % (self.name, self.backup_format)
        return database.database_backup(
            backup_name=name,
            keep_till_date=self.keep_till_date,
            backup_format=self.backup_format
        )
