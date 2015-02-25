# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from erppeek import Client
from openerp.exceptions import Warning


class Contract(models.Model):
    _inherit = 'support.contract'
    _description = 'support.contract'

    @api.one
    def get_documentation_data(self):
        client = self.get_connection()
        installed_modules = self.env['ir.module.module'].search(
            [('state', '=', 'installed')])
        installed_module_names = [x.name for x in installed_modules]
        # toc_ids = client.model('website.doc.toc').search(
        #     [('external_id', '!=', False),
        #     ('required_module_id.name', 'in', installed_module_names)])
        # client.model('website.doc.toc').read()
        doc_data = client.read(
            'website.doc.toc',
            [('external_id', '!=', False),
             ('required_module_id.name', 'in', installed_module_names)])
        print 'doc_data', doc_data
        # TODO implementar aca
        # fields = [
        #     'id',
        #     'database_id/.id',
        #     'date',
        #     'name',
        #     'path',
        #     'type',
        #     ]
        # rows = []
        # for backup in backups_data:
        #     row = [
        #         'db_%i_backup_%i' % (self.id, backup['id']),
        #         self.id,
        #         backup['date'],
        #         backup['name'],
        #         backup['path'],
        #         backup['type'],
        #     ]
        #     rows.append(row)
        # self.env['infrastructure.database.backup'].load(fields, rows)
        # self.get_connection()
        raise Warning(_('Not implemented yet!'))

    # @api.multi
    # def get_connection(self):
    #     self.ensure_one()
    #     db_list = self.get_client().db.list()
    #     if db_list:
    #         return self.get_client(db_list[0])
    #     else:
    #         raise Warning(_("Could not fine any database on socket '%s'") % (
    #             self.server_host))

    # @api.multi
    # def get_client(self, database=False):
    #     self.ensure_one()
    #     try:
    #         if not database:
    #             return Client(
    #                 'http://%s' % (self.server_host))
    #         else:
    #             return Client(
    #                 'http://%s' % (self.server_host),
    #                 db=database,
    #                 user=self.user,
    #                 password=self.number)
    #     except Exception, e:
    #         raise Warning(
    #             _("Unable to Connect to Server. Check that in db '%s' module\
    #              'web_support_server' is installed and user '%s' exists and\
    #              has a contract with code '%s'. This is what we get: %s") % (
    #                 database, self.user, self.number, e)
    #         )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
