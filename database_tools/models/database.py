# -*- encoding: utf-8 -*-
import os
import shutil
import base64
from datetime import datetime
from datetime import date
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
    backup_rule_type = fields.Selection([
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
        """Check if backups exists on filesyste, if not, unlink records"""
        for backup in self.backup_ids:
            if not os.path.isfile(backup.full_path):
                backup.unlink()
        return True

    @api.one
    def drop_con(self):
        """Drop connections. This is used when can not make backups.
        Usually in instances with workers.
        """
        db_ws._drop_conn(self._cr, self.name)
        # Por si no anda...
        # db = sql_db.db_connect('postgres')
        # with closing(db.cursor()) as pg_cr:
        #     pg_cr.autocommit(True)     # avoid transaction block
        #     db_ws._drop_conn(pg_cr, self.name)
        return True

    @api.one
    @api.constrains('type', 'not_self_name')
    def _check_db_exist(self):
        """Checks if database exists"""
        if self.type != 'self' and not db_ws.exp_db_exist(self.not_self_name):
            raise Warning(_('Database %s do not exist') % (self.not_self_name))

    @api.model
    def cron_database_backup(self):
        """If backups enable in ir parameter, then:
        * Check if backups are enable
        * Make backup according to period defined
        * """
        backups_enable = self.env['ir.config_parameter'].get_param(
                'database.backups.enable')
        if backups_enable != 'True':
            _logger.warning(
                'Backups are disable. If you want to enable it you should add the parameter database.backups.enable with value True')
            return False
        _logger.info('Running backups cron')
        current_date = time.strftime('%Y-%m-%d')
        # get databases
        databases = self.search([
            ('backup_next_date', '<=', current_date),
            ])

        # make bakcup
        databases.database_backup('automatic')

        # clean databases
        databases = self.search([])
        databases.database_backup_clean('automatic')

        # clean databas information
        self.update_backups_data()

    @api.model
    def relative_delta(self, from_date, interval, rule_type):
        if rule_type == 'daily':
            next_date = from_date+relativedelta(days=+interval)
        elif rule_type == 'weekly':
            next_date = from_date+relativedelta(weeks=+interval)
        elif rule_type == 'monthly':
            next_date = from_date+relativedelta(months=+interval)
        else:
            raise Warning('Type must be one of "days, weekly or monthly"')
        return next_date

    @api.one
    def action_database_backup_clean(self):
        """Action to be call from buttons"""
        _logger.info('Action database backup clean called manually')
        res = self.database_backup_clean()
        return res

    @api.multi
    def database_backup_clean(self, bu_type=None):
        term_to_date = date.today()
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
                        interval_from_date, interval_to_date, self.ids))
                domain = [
                    ('database_id', 'in', self.ids),
                    ('date', '>', interval_from_date.strftime('%Y-%m-%d')),
                    ('date', '<=', interval_to_date.strftime('%Y-%m-%d')),
                    ]
                if bu_type:
                    domain.append(('type', '=', bu_type))
                backup = self.env['db.database.backup'].search(
                    domain, order='date', limit=1)
                if backup:
                    _logger.info('Found backups ids %s', backup.id)
                    preserve_backups_ids.append(backup.id)
                else:
                    _logger.info('No backups found')
                interval_from_date = interval_to_date
        _logger.info('Backups to preserve ids %s', preserve_backups_ids)
        to_delete_backups = self.env['db.database.backup'].search(
            [('id', 'not in', preserve_backups_ids)])
        _logger.info('Backups to delete ids %s', to_delete_backups.ids)

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
                    else:
                        backup.close()
                        database.backup_ids.create({
                            'database_id': database.id,
                            'name': backup_name,
                            'path': database.backups_path,
                            'date': now,
                            'type': bu_type,
                            })
                        _logger.info('Backup %s Created' % backup_name)

                        if bu_type == 'automatic':
                            _logger.info('Reconfiguring next backup')
                            new_date = self.relative_delta(
                                date.today(),
                                self.backup_interval,
                                self.backup_rule_type)
                            database.backup_next_date = new_date

                        _logger.info('Backup %s Created' % backup_name)

                        # TODO check gdrive backup pat
                        if self.syncked_backup_path:
                            _logger.info('Make backup a copy con syncked path')
                            try:
                                syncked_backup = os.path.join(
                                    database.syncked_backup_path,
                                    self.name + '.zip')
                                shutil.copy2(backup_path, syncked_backup)
                            except Exception, e:
                                error = "Could not copy into syncked folder.\
                                    This is what we get:\n\
                                    %s" % (e)
                                _logger.warning(error)
            if error:
                res[database.name] = {'error': error}
            else:
                res[database.name] = {'backup_name': backup_name}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
