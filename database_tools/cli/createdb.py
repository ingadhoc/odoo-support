# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
import signal
import openerp
import openerp.tools.config as config
from openerp.cli import Command

from openerp.cli.server import main
from openerp.service.db import _create_empty_database, DatabaseExists

_logger = logging.getLogger(__name__)


def raise_keyboard_interrupt(*a):
    raise KeyboardInterrupt()


class Createdb(Command):
    def init(self, args):
        openerp.tools.config.parse_config(args)
        openerp.cli.server.report_configuration()
        openerp.service.server.start(preload=[], stop=True)
        signal.signal(signal.SIGINT, raise_keyboard_interrupt)

    def run(self, args):
        self.init(args)
        db_name = config['db_name']
        if not db_name:
            print (
                "Could not create database, no database on odoo conf or as "
                "argument")
            return 1
        try:
            _create_empty_database(db_name)
            if "--stop-after-init" not in args:
                args.append('--stop-after-init')
            main(args)
        except DatabaseExists, e:
            print ("Database '%s' already exsists" % db_name)
        except Exception, e:
            print ("Could not create database `%s`. (%s)" % (db_name, e))
            return 1
        return 0
