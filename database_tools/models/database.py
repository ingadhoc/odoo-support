# -*- encoding: utf-8 -*-
import os
import base64
from datetime import datetime
from openerp import fields, models, api, _, modules
from openerp.exceptions import Warning
from openerp.service import db as db_ws
from dateutil.relativedelta import relativedelta
import time
import logging
_logger = logging.getLogger(__name__)


class db_database(models.Model):

    _name = 'db.database'

    @api.model
    def _get_default_name(self):
        return self._cr.dbname

    not_self_name = fields.Char(
        'Database',
        default=_get_default_name,
        )
    name = fields.Char(
        'Database',
        compute='_get_name',
        )
    type = fields.Selection(
        [('self', 'Self'), ('other', 'Local')],
        string='Type',
        required=True,
        default='self',
        )
    syncked_backup_path = fields.Char(
        string='Sicked Backup Path',
        default='/var/odoo/backups/',
        help='If defined, after each backup, a copy backup with database name as file name, will be saved on this folder'
        )
    backups_path = fields.Char(
        string='Backups Path',
        required=True,
        default='/var/odoo/backups/',
        help='User running this odoo intance must have CRUD access rights on this folder'
        # TODO agregar boton para probar que se tiene permisos
        )
    backup_next_date = fields.Date(
        string='Date of Next Backup',
        default=fields.Date.context_today,
        required=True,
        )
    backup_rule_type = fields.selection([
        ('daily', 'Day(s)'),
        ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'),
        ('yearly', 'Year(s)'),
        ], 'Recurrency',
        help="Backup automatically repeat at specified interval",
        default='daily',
        )
    backup_interval = fields.Integer(
        string='Repeat Every',
        default=1,
        required=True,
        help="Repeat every (Days/Week/Month/Year)"
        )
    backup_ids = fields.One2many(
        'db.database.backup',
        'database_id',
        string='Backups',
        readonly=True,
        )
    backup_count = fields.Integer(
        string='# Backups',
        compute='_get_backups'
        )

    @api.one
    @api.depends('type', 'not_self_name')
    def _get_name(self):
        name = self.not_self_name
        if self.type == 'self':
            name = self._cr.dbname
        self.name = name

    @api.one
    @api.depends('backup_ids')
    def _get_backups(self):
        self.backup_count = len(self.backup_ids)

    @api.model
    def backups_state(self, db_name, state_type):
        registry = modules.registry.RegistryManager.get(db_name)
        with registry.cursor() as db_cr:
            registry['ir.config_parameter'].set_param(
                db_cr, 1, 'database.backups.enable', str(state_type))
        return True

    @api.multi
    def update_backups_data(self):
        self.ensure_one()
        for backup in self.backup_ids:
            if not os.path.isfile(backup.full_path):
                backup.unlink()
        return True

    @api.multi
    def drop_con(self):
        self.ensure_one()
        db_ws._drop_conn(self._cr, self.name)
        # Por si no anda...
        # db = sql_db.db_connect('postgres')
        # with closing(db.cursor()) as pg_cr:
        #     pg_cr.autocommit(True)     # avoid transaction block
        #     db_ws._drop_conn(pg_cr, self.name)
        return True

    @api.one
    @api.constrains('type')
    def _check_type(self):
        if self.type == 'remote':
            raise Warning(_('Type Remote not implemented yet'))

    @api.one
    @api.constrains('type', 'not_self_name')
    def _check_db_exist(self):
        if self.type != 'self' and not db_ws.exp_db_exist(self.not_self_name):
            raise Warning(_('Database %s do not exist') % (self.not_self_name))

    @api.model
    def cron_database_backup(self):
        backups_enable = self.env['ir.config_parameter'].get_param(
                'database.backups.enable')
        if backups_enable != 'True':
            _logger.warning(
                'Backups are disable. If you want to enable it you should add the parameter database.backups.enable with value True')
            return False
        _logger.info('Running backups cron')
        current_date = time.strftime('%Y-%m-%d')
        daily_databases = self.search([
            ('daily_backup', '=', True),
            ('daily_next_date', '<=', current_date),
            ])
        daily_databases.database_backup('daily')
        weekly_databases = self.search([
            ('weekly_backup', '=', True),
            ('weekly_next_date', '<=', current_date),
            ])
        weekly_databases.database_backup('weekly')
        monthly_databases = self.search([
            ('monthly_backup', '=', True),
            ('monthly_next_date', '<=', current_date),
            ])
        monthly_databases.database_backup('monthly')
        # clean databases
        databases = self.search([])
        databases.database_backup_clean('daily')
        databases.database_backup_clean('weekly')
        databases.database_backup_clean('monthly')

    @api.one
    def database_backup_clean(self, bu_type='daily'):
        current_date = time.strftime('%Y-%m-%d')
        from_date = datetime.strptime(current_date, '%Y-%m-%d')
        if bu_type == 'daily':
            interval = self.daily_save_periods
            from_date = from_date+relativedelta(days=-interval)
        elif bu_type == 'weekly':
            interval = self.weekly_save_periods
            from_date = from_date+relativedelta(weeks=-interval)
        elif bu_type == 'monthly':
            interval = self.monthly_save_periods
            from_date = from_date+relativedelta(months=-interval)

        from_date = from_date.strftime('%Y-%m-%d')
        databases = self.env['db.database.backup'].search([
            ('database_id', '=', self.id),
            ('type', '=', bu_type),
            ('date', '<=', from_date),
            ])
        for database in databases:
            database.unlink()

    @api.multi
    def action_database_backup(self):
        """Action to be call from buttons"""
        _logger.info('Action database backup called manually')
        res = self.database_backup('manual')
        return res

    @api.multi
    def database_backup(self, bu_type):
        """Returns a dictionary where:
        * keys = database name
        * value = dictionary with:
            * key error and error as value
            * key database and database name as value
        """
        now = datetime.now()
        res = {}
        for database in self:
            error = False
            backup_name = False
            # check if bd exists
            try:
                if not db_ws.exp_db_exist(database.name):
                    error = "Database %s do not exist" % (database.name)
                    _logger.warning(error)
            except Exception, e:
                error = "Could not check if database %s exists. This is what we get:\n\
                    %s" % (database.name, e)
                _logger.warning(error)
            else:
                # crear path para backups si no existe
                try:
                    if not os.path.isdir(database.backups_path):
                        os.makedirs(database.backups_path)
                except Exception, e:
                    error = "Could not create folder %s for backups.\
                        This is what we get:\n\
                        %s" % (database.backups_path, e)
                    _logger.warning(error)
                else:
                    backup_name = '%s_%s_%s.zip' % (
                        database.name, bu_type, now.strftime('%Y%m%d_%H%M%S'))
                    backup_path = os.path.join(
                        database.backups_path, backup_name)
                    backup = open(backup_path, 'wb')
                    # backup
                    try:
                        backup.write(base64.b64decode(
                            db_ws.exp_dump(database.name)))
                    except:
                        error = 'Unable to dump Database. If you are working in an\
                                instance with "workers" then you can try \
                                restarting service.'
                        _logger.warning(error)
                        backup.close()
                    backup.close()
                    database.backup_ids.create({
                        'database_id': database.id,
                        'name': backup_name,
                        'path': database.backups_path,
                        'date': now,
                        'type': bu_type,
                        })

                    current_date = time.strftime('%Y-%m-%d')
                    next_date = datetime.strptime(current_date, '%Y-%m-%d')
                    interval = 1
                    if bu_type == 'daily':
                        new_date = next_date+relativedelta(days=+interval)
                        database.daily_next_date = new_date
                    elif bu_type == 'weekly':
                        new_date = next_date+relativedelta(weeks=+interval)
                        database.weekly_next_date = new_date
                    elif bu_type == 'monthly':
                        new_date = next_date+relativedelta(months=+interval)
                        database.monthly_next_date = new_date
                    _logger.info('Backup %s Created' % backup_name)

            if error:
                res[database.name] = {'error': error}
            else:
                res[database.name] = {'backup_name': backup_name}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
