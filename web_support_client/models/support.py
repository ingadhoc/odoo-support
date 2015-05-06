# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from erppeek import Client
from openerp.exceptions import Warning


class Contract(models.Model):
    _name = 'support.contract'
    _description = 'support.contract'

    name = fields.Char(
        'Name',
        required=True,
        )
    user = fields.Char(
        'User',
        required=True,
        )
    database = fields.Char(
        'Database',
        help='Support Database. If any configured, first database will be used',
        )
    server_host = fields.Char(
        string='Server Host',
        required=True,
        help="Specified the port if port different from 80. For eg you can use: \
        * ingadho.com\
        * ingadhoc.com:8069"
        )
    number = fields.Char(
        string='Number',
        required=True,
        )

    @api.multi
    def get_connection(self):
        """Function to get erpeek client"""

        self.ensure_one()
        if not self.database:
            db_list = self.get_client().db.list()
            if db_list:
                return self.get_client(db_list[0])
            else:
                raise Warning(_("Could not fine any database on socket '%s'") % (
                    self.server_host))
        else:
            return self.get_client(self.database)

    @api.multi
    def get_client(self, database=False):
        """You should not use this function directly, you sould call
        get_connection"""

        self.ensure_one()
        try:
            if not database:
                return Client(self.server_host)
            else:
                return Client(
                    self.server_host,
                    db=database,
                    user=self.user,
                    password=self.number)
        except Exception, e:
            raise Warning(
                _("Unable to Connect to Server. Check that in db '%s' module\
                 'web_support_server' is installed and user '%s' exists and\
                 has a contract with code '%s'. This is what we get: %s") % (
                    database, self.user, self.number, e)
            )

    @api.multi
    def check_state(self):
        self.ensure_one()
        return self.get_connection()

    @api.model
    def get_active_contract(self):
        """Funcion que permitiria incorporar estados en los contratos y
        devolver uno activo"""
        active_contract = self.search([], limit=1)
        if not active_contract:
            raise Warning(_('No active contract configured'))
        return active_contract

    @api.multi
    def get_remote_contract(self):
        """
        """
        self.ensure_one()
        client = self.get_connection()
        contract = client.model('account.analytic.account').browse(
            [('code', '=', self.number)], limit=1)
        return contract

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
