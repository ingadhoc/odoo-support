# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import openerp.http as http
import base64
from openerp import _
import openerp
from openerp.service import db as db_ws
from contextlib import closing
import os
import logging
import zipfile
# import werkzeug

try:
    from fabric.api import env
except ImportError:
    env = None

try:
    from fabric.operations import get
except ImportError:
    get = None

_logger = logging.getLogger(__name__)


def exp_drop_only_db(db_name):
    openerp.modules.registry.RegistryManager.delete(db_name)
    openerp.sql_db.close_db(db_name)

    db = openerp.sql_db.db_connect('postgres')
    with closing(db.cursor()) as cr:
        cr.autocommit(True)     # avoid transaction block
        db_ws._drop_conn(cr, db_name)

        try:
            cr.execute('DROP DATABASE "%s"' % db_name)
        except Exception, e:
            _logger.error('DROP DB: %s failed:\n%s', db_name, e)
            raise Exception("Couldn't drop database %s: %s" % (db_name, e))
        else:
            _logger.info('DROP DB: %s', db_name)
    return True


class db_tools(http.Controller):

    # implemented like cli
    # @http.route(
    #     '/fix_db/<string:db_name>',
    #     type='http',
    #     auth='none',
    # )
    # def fix_db(self, db_name):
    #     registry = openerp.modules.registry.RegistryManager.get(db_name)
    #     _logger.info("Fix database %s called from controller!" % db_name)
    #     cr = registry.cursor()
    #     registry['db.configuration'].fix_db(cr, 1)
    #     return werkzeug.utils.redirect("/")

    @http.route(
        '/restore_db',
        type='json',
        auth='none',
    )
    def restore_db(
            self, admin_pass, db_name, file_path, file_name,
            backups_state, remote_server=False, overwrite=False):
        _logger.info(
            "Starting restore process with data:\n"
            "* db_name: %s\n"
            "* file_path: %s\n"
            "* file_name: %s\n"
            "* backups_state: %s\n"
            "* remote_server: %s\n" % (
                db_name, file_path, file_name, backups_state, remote_server))
        database_file = os.path.join(file_path, file_name)
        if remote_server:
            local_path = '/opt/odoo/backups/tmp/'
            user_name = remote_server.get('user_name')
            password = remote_server.get('password')
            host_string = remote_server.get('host_string')
            port = remote_server.get('port')
            if not user_name or not password or not host_string or not port:
                return {'error': (
                    'You need user_name, password, host_string'
                    'and port in order to use remote_server')}
            env.user = user_name
            env.password = password
            env.host_string = host_string
            env.port = port
            _logger.info("Getting file '%s' from '%s:%s' with user %s" % (
                database_file, host_string, port, user_name))
            res = get(
                remote_path=database_file,
                local_path=local_path,
                use_sudo=True)
            if not res.succeeded:
                return {'error': 'Could not copy file from remote server'}
            database_file = os.path.join(local_path, file_name)

        _logger.info(
            "Restoring database %s from %s" % (db_name, database_file))
        error = False
        if overwrite:
            if db_name not in db_ws.exp_list(True):
                _logger.info(
                    "Overwrite argument passed but db %s not found, "
                    "avoiding db drop" % db_name)
            else:
                # if overwrite, then we delete actual db first
                _logger.info(
                    "Overwrite argument passed, deleting db %s" % db_name)
                if zipfile.is_zipfile(database_file):
                    # if zip, then we just use dropd
                    db_ws.exp_drop(db_name)
                    _logger.info("Db %s deleted completely" % db_name)
                else:
                    # if not zip, we keep filestore
                    exp_drop_only_db(db_name)
                    _logger.info(
                        "Db %s deleted (only db, no filestore)" % db_name)
        try:
            _logger.info("Reading file for restore")
            f = file(database_file, 'r')
            data_b64 = base64.encodestring(f.read())
            f.close()
        except Exception, e:
            error = (_(
                'Unable to read file %s\n'
                'This is what we get: \n %s') % (
                database_file, e))
            return {'error': error}
        try:
            _logger.info("Restoring....")
            db_ws.exp_restore(db_name, data_b64)
        except Exception, e:
            # TODO ver si odoo arreglo esto si el error contiene "error 1" y
            # no es un zip, entonces es un error de odoo pero que no es error
            # en realidad
            if not zipfile.is_zipfile(database_file):
                _logger.info(
                    "We found an error restoring pg_dump but it seams to be an"
                    "Please check database created correctly. Error:\n%s" % (
                        e))
            else:
                error = (_(
                    'Unable to restore bd %s, this is what we get: \n %s') % (
                    db_name, e))
                return {'error': error}

        _logger.info("Databse %s restored succesfully!" % db_name)
        # # disable or enable backups
        # TODO unificar con la que esta en database
        registry = openerp.modules.registry.RegistryManager.get(db_name)
        _logger.info("Disable/Enable Backups on %s!" % db_name)
        with registry.cursor() as db_cr:
            registry['ir.config_parameter'].set_param(
                db_cr, 1, 'database.backups.enable', str(backups_state))
        return {}
