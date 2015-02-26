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
        help='',
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
        self.ensure_one()
        try:
            if not database:
                return Client(
                    'http://%s' % (self.server_host))
            else:
                return Client(
                    'http://%s' % (self.server_host),
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

    @api.one
    def get_state(self):
        self.get_connection()
        raise Warning(_('Not implemented yet!'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
