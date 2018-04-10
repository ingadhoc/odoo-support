import logging
import signal
import odoo
import odoo.tools.config as config
from odoo.api import Environment
from odoo.cli import Command
_logger = logging.getLogger(__name__)


def raise_keyboard_interrupt(*a):
    raise KeyboardInterrupt()


class Fixdb(Command):

    def init(self, args):
        odoo.tools.config.parse_config(args)
        odoo.cli.server.report_configuration()
        odoo.service.server.start(preload=[], stop=True)
        signal.signal(signal.SIGINT, raise_keyboard_interrupt)

    def fixdb(self, dbname):
        with Environment.manage():
            if config['db_name']:
                db_names = config['db_name'].split(',')
            else:
                db_names = odoo.service.db.list_dbs(True)
            for dbname in db_names:
                _logger.info('Running fix for database %s' % dbname)
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    uid = odoo.SUPERUSER_ID
                    ctx = Environment(cr, uid, {})['res.users'].context_get()
                    env = Environment(cr, uid, ctx)
                    _logger.info('Fixing database started')
                    # no formzamos desinstalación por las dudas de que haya
                    # un error en la clasificación de adhoc modules o en datos
                    # (los script de los modulos deberian ser quien se
                    # encarguen de limpiar si corresponde)
                    env['db.configuration'].fix_db(uninstall_modules=False)
                    _logger.info('Fixing database finished')

    def run(self, args):
        self.init(args)
        try:
            self.fixdb(odoo.tools.config['db_name'])
        except Exception as e:
            _logger.warning('Could not fix dbs, this is what we get %s' % e)
        return 0
