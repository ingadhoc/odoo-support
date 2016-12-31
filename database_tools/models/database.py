# -*- encoding: utf-8 -*-
import os
import shutil
from datetime import datetime
from openerp import fields, models, api, _, modules
from openerp.exceptions import ValidationError
from openerp.service import db as db_ws
from dateutil.relativedelta import relativedelta
from openerp.addons.server_mode.mode import get_mode
import logging
_logger = logging.getLogger(__name__)


class db_database(models.Model):

    _name = 'db.database'

    @api.model
    def _get_default_name(self):
        return self._cr.dbname

    @api.model
    def _get_preserve_rules(self):
        return self.env['db.database.backup.preserve_rule'].search([])

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
        string='Sincked Backup Path',
        default='/var/odoo/backups/syncked/',
        help='If defined, after each backup, a copy backup with database name '
        'as file name, will be saved on this folder'
    )
    # we dont make it optionally because it requires a dificult update
    # on production databases of this module
    # remove_unlisted_files = fields.Boolean(
    #     help='Remove any file in "Backups Path" that is not '
    #     'a listed backup',
    #     default=True,
    # )
    backups_path = fields.Char(
        string='Backups Path',
        required=True,
        default='/var/odoo/backups/',
        help='User running this odoo intance must have CRUD access rights on '
        'this folder. Warning, every file on this folder will be removed'
        # TODO add button to check rights on path
    )
    backup_next_date = fields.Datetime(
        string='Date of Next Backup',
        default=fields.Datetime.now,
        # default=fields.Date.context_today,
        # TODO change default so it takes a value on early morning, something
        # like: datetime.strftime(datetime.today()+timedelta(days=1),
        # '%Y-%m-%d 05:%M:%S')
        required=True,
    )
    backup_rule_type = fields.Selection([
        ('hourly', 'Hour(s)'),
        ('daily', 'Day(s)'),
        ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'),
        ('yearly', 'Year(s)'),
    ],
        'Recurrency',
        help="Backup automatically repeat at specified interval",
        default='daily',
        required=True,
    )
    backup_format = fields.Selection([
        ('zip', 'zip (With Filestore)'),
        ('pg_dump', 'pg_dump (Without Filestore)')],
        'Backup Format',
        default='zip',
        required=True,
    )
    backup_interval = fields.Integer(
        string='Repeat Every',
        default=1,
        required=True,
        help="Repeat every (Days/Week/Month/Year)"
    )
    backup_preserve_rule_ids = fields.Many2many(
        'db.database.backup.preserve_rule',
        'db_backup_preserve_rule_rel',
        'database_id', 'preserve_rule_id',
        'Preservation Rules',
        required=True,
        default=_get_preserve_rules,
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

    @api.model
    def get_overall_backups_state(self):
        res = {
            'state': 'ok',
            'detail': False,
        }
        backups_state = self.search([]).get_backups_state()
        if backups_state:
            res['state'] = 'error'
            res['detail'] = 'Backups errors:\n%s' % backups_state
        return res

    @api.multi
    def get_backups_state(self):
        """
        """
        res = {}
        for database in self:
            database.update_backups_data()
            # we use now instead o next, because if backups
            # are off, next date wont be updated

            next_date = datetime.now()
            # we give a tolerance of two periods
            tolerance = 2
            interval = -database.backup_interval
            rule_type = database.backup_rule_type
            from_date = database.relative_delta(
                next_date,
                interval * tolerance,
                rule_type)

            backups = self.env['db.database.backup'].search([
                ('database_id', '=', database.id),
                ('date', '>=', fields.Datetime.to_string(from_date)),
                ('type', '=', 'automatic'),
            ])

            if not backups:
                res[database.id] = (
                    'No backups for database id %i from date %s till now.'
                    ' Parameters:\n'
                    ' * Tolerance: %s periods\n'
                    ' * Interval: %s\n'
                    ' * Rule Type: %s\n'
                    ' * Next Date: %s\n' % (
                        database.id, from_date,
                        tolerance,
                        interval,
                        rule_type,
                        next_date))
        return res

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
        """Update ir parameter to enable or disable backups"""
        registry = modules.registry.RegistryManager.get(db_name)
        with registry.cursor() as db_cr:
            registry['ir.config_parameter'].set_param(
                db_cr, 1, 'database.backups.enable', str(state_type))
        return True

    @api.one
    def update_backups_data(self):
        """Check if backups exists on filesystem, if not, unlink records"""
        for backup in self.backup_ids:
            if not os.path.isfile(backup.full_path):
                backup.unlink()
        return True

    @api.one
    def drop_con(self):
        """
        Drop connections. This is used when can not make backups.
        Usually in instances with workers.
        """
        db_ws._drop_conn(self._cr, self.name)
        # Por si no anda...
        # db = sql_db.db_connect('postgres')
        # with closing(db.cursor()) as pg_cr:
        # pg_cr.autocommit(True)     # avoid transaction block
        #     db_ws._drop_conn(pg_cr, self.name)
        return True

    @api.one
    @api.constrains('type', 'not_self_name')
    def _check_db_exist(self):
        """Checks if database exists"""
        if self.type != 'self' and not db_ws.exp_db_exist(self.not_self_name):
            raise ValidationError(_(
                'Database %s do not exist') % (self.not_self_name))

    @api.model
    def check_automatic_backup_enable(self):
        """
        Para que se hagan backups al hacer fix on con el cron, se requiere:
        1. Que no haya server mode definido
        2. Que haya un parametro database.backups.enable = 'True'
        """
        if get_mode():
            _logger.info(
                'Backups are disable by server_mode test or develop. '
                'If you want to enable it you should remove develop or test '
                'value for server_mode key on openerp server config file')
            return False
        backups_enable = self.env['ir.config_parameter'].get_param(
            'database.backups.enable')
        if backups_enable != 'True':
            _logger.info(
                'Backups are disable. If you want to enable it you should add '
                'the parameter database.backups.enable with value True')
            return False
        return True

    @api.model
    def cron_database_backup(self):
        """If backups enable in ir parameter, then:
        * Check if backups are enable
        * Make backup according to period defined
        * """
        if not self.check_automatic_backup_enable():
            return False
        _logger.info('Running backups cron')
        current_date = fields.Datetime.now()
        # get databases
        databases = self.search([
            ('backup_next_date', '<=', current_date),
        ])

        # make bakcup
        # we make a loop to commit after each backup
        for database in databases:
            database.database_backup(
                bu_type='automatic',
                backup_format=database.backup_format)
            database._cr.commit()

        # clean databases
        databases = self.search([])

        databases.database_backup_clean()

        # clean databas information
        self.update_backups_data()

    @api.model
    def relative_delta(self, from_date, interval, rule_type):
        if rule_type == 'hourly':
            next_date = from_date + relativedelta(hours=+interval)
        elif rule_type == 'daily':
            next_date = from_date + relativedelta(days=+interval)
        elif rule_type == 'weekly':
            next_date = from_date + relativedelta(weeks=+interval)
        elif rule_type == 'monthly':
            next_date = from_date + relativedelta(months=+interval)
        else:
            raise ValidationError(
                'Type must be one of "days, weekly or monthly"')
        return next_date

    @api.one
    def action_database_backup_clean(self):
        """Action to be call from buttons"""
        _logger.info('Action database backup clean called manually')
        res = self.database_backup_clean()
        return res

    @api.multi
    def database_backup_clean(self, bu_type=None):
        """If bu_type is:
        * none, then clean will affect automatic and manual backups
        * automatic or manual. only backups of that type are going to be clean
        """
        if not bu_type or bu_type == 'manual':
            self.database_manual_backup_clean()

        if not bu_type or bu_type == 'automatic':
            self.database_auto_backup_clean()

        self.action_remove_unlisted_files()

    @api.multi
    def action_remove_unlisted_files(self):
        _logger.info('Removing unlisted files')
        for db in self:
            # if not db.remove_unlisted_files:
            #     continue
            backups_paths = db.mapped('backup_ids.name')
            for directory in os.listdir(db.backups_path):
                if directory not in backups_paths:
                    self.remove_directory(
                        os.path.join(db.backups_path, directory))

    @api.model
    def remove_directory(self, directory):
        try:
            os.remove(directory)
            _logger.info('File %s removed succesfully' % directory)
        except Exception, e:
            _logger.warning(
                'Unable to remoove database file on %s, '
                'this is what we get:\n'
                '%s' % (directory, e.strerror))

    @api.multi
    def database_manual_backup_clean(self):
        _logger.info('Runing Manual Backups Clean')
        domain = [
            ('database_id', 'in', self.ids),
            ('keep_till_date', '<=', fields.Datetime.now()),
        ]
        to_delete_backups = self.env['db.database.backup'].search(
            domain)
        to_delete_backups.unlink()

    @api.one
    def database_auto_backup_clean(self):
        _logger.info('Runing Automatic Backups Clean')
        # automatic backups
        term_to_date = datetime.now()
        preserve_backups_ids = []
        for rule in self.backup_preserve_rule_ids:
            term_from_date = self.relative_delta(
                term_to_date, -rule.term, rule.term_type)
            interval_from_date = term_from_date
            _logger.info(
                'Searchig for backups to preserve. Rule: %s, from %s to %s' % (
                    rule.name, term_from_date, term_to_date))
            while interval_from_date <= term_to_date:
                interval_to_date = self.relative_delta(
                    interval_from_date, rule.interval, rule.interval_type)
                _logger.info(
                    'Searching for backups in %s / %s on databases %s' % (
                        interval_from_date, interval_to_date, self.id))
                domain = [
                    ('database_id', '=', self.id),
                    ('date', '>', fields.Datetime.to_string(
                        interval_from_date)),
                    ('date', '<=', fields.Datetime.to_string(
                        interval_to_date)),
                    ('type', '=', 'automatic'),
                ]
                backup = self.env['db.database.backup'].search(
                    domain, order='date', limit=1)
                if backup:
                    _logger.info('Found backups ids %s', backup.id)
                    preserve_backups_ids.append(backup.id)
                else:
                    _logger.info('No backups found')
                interval_from_date = interval_to_date
        _logger.info('Backups to preserve ids %s', preserve_backups_ids)
        to_delete_backups = self.env['db.database.backup'].search([
            ('id', 'not in', preserve_backups_ids),
            ('type', '=', 'automatic'),
            ('database_id', '=', self.id),
        ])
        _logger.info('Backups to delete ids %s', to_delete_backups.ids)
        # to_delete_backups.unlink()
        # we make a loop to commit after each delete
        for backup in to_delete_backups:
            backup.unlink()
            backup._cr.commit()
        return True

    @api.multi
    def database_backup(
            self, bu_type='manual',
            backup_format='zip', backup_name=False, keep_till_date=False):
        """Returns a dictionary where:
        * keys = database name
        * value = dictionary with:
            * key error and error as value
            * key database and database name as value
        """
        self.ensure_one()

        now = datetime.now()
        error = False

        # check if bd exists
        try:
            if not db_ws.exp_db_exist(self.name):
                error = "Database %s do not exist" % (self.name)
                _logger.warning(error)
        except Exception, e:
            error = (
                "Could not check if database %s exists. "
                "This is what we get:\n"
                "%s" % (self.name, e))
            _logger.warning(error)
        else:
            # crear path para backups si no existe
            try:
                if not os.path.isdir(self.backups_path):
                    os.makedirs(self.backups_path)
            except Exception, e:
                error = (
                    "Could not create folder %s for backups. "
                    "This is what we get:\n"
                    "%s" % (self.backups_path, e))
                _logger.warning(error)
            else:
                if not backup_name:
                    backup_name = '%s_%s_%s.%s' % (
                        self.name,
                        bu_type,
                        now.strftime('%Y%m%d_%H%M%S'),
                        backup_format)
                backup_path = os.path.join(
                    self.backups_path, backup_name)
                if os.path.isfile(backup_path):
                    return {'error': "File %s already exists" % backup_path}
                backup = open(backup_path, 'wb')
                # backup
                try:
                    db_ws.dump_db(
                        self.name,
                        backup,
                        backup_format=backup_format)
                except Exception, e:
                    error = (
                        'Unable to dump self. '
                        'If you are working in an instance with '
                        '"workers" then you can try restarting service.\n'
                        'This is what we get: %s' % e)
                    _logger.warning(error)
                    backup.close()
                else:
                    backup.close()
                    backup_vals = {
                        'database_id': self.id,
                        'name': backup_name,
                        'path': self.backups_path,
                        'date': now,
                        'type': bu_type,
                        'keep_till_date': keep_till_date,
                    }
                    self.backup_ids.create(backup_vals)
                    _logger.info('Backup %s Created' % backup_name)

                    if bu_type == 'automatic':
                        _logger.info('Reconfiguring next backup')
                        new_date = self.relative_delta(
                            datetime.now(),
                            self.backup_interval,
                            self.backup_rule_type)
                        self.backup_next_date = new_date

                    # TODO check gdrive backup pat
                    if self.syncked_backup_path:
                        # so no existe el path lo creamos
                        try:
                            if not os.path.isdir(
                                    self.syncked_backup_path):
                                _logger.info(
                                    'Creating syncked backup folder')
                                os.makedirs(self.syncked_backup_path)
                        except Exception, e:
                            error = (
                                "Could not create folder %s for backups. "
                                "This is what we get:\n"
                                "%s" % (self.syncked_backup_path, e))
                            _logger.warning(error)

                        # now we copy the backup
                        _logger.info('Make backup a copy con syncked path')
                        try:
                            syncked_backup = os.path.join(
                                self.syncked_backup_path,
                                self.name + '.%s' % backup_format)
                            shutil.copy2(backup_path, syncked_backup)
                        except Exception, e:
                            error = (
                                "Could not copy into syncked folder. "
                                "This is what we get:\n"
                                "%s" % (e))
                            _logger.warning(error)
        if error:
            return {'error': error}
        else:
            return {'backup_name': backup_name}
