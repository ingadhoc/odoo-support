# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
import signal
import openerp
import openerp.tools.config as config
from openerp.api import Environment
from openerp.cli import Command

_logger = logging.getLogger(__name__)


def raise_keyboard_interrupt(*a):
    raise KeyboardInterrupt()


class Fixdb(Command):
    """Start odoo in an interactive shell"""
    def init(self, args):
        openerp.tools.config.parse_config(args)
        openerp.cli.server.report_configuration()
        openerp.service.server.start(preload=[], stop=True)
        signal.signal(signal.SIGINT, raise_keyboard_interrupt)

    def fixdb(self, dbname):
        with Environment.manage():
            if config['db_name']:
                db_names = config['db_name'].split(',')
            else:
                db_names = openerp.service.db.list_dbs(True)
            for dbname in db_names:
                _logger.info('Running fix for tabase %s' % dbname)
                registry = openerp.modules.registry.RegistryManager.get(dbname)
                with registry.cursor() as cr:
                    uid = openerp.SUPERUSER_ID
                    ctx = Environment(cr, uid, {})['res.users'].context_get()
                    env = Environment(cr, uid, ctx)
                    _logger.info('Fixing database started')
                    env['db.configuration'].fix_db(uninstall_modules=True)
                    _logger.info('Fixing database finished')

    def run(self, args):
        self.init(args)
        self.fixdb(openerp.tools.config['db_name'])
        return 0
