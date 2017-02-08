# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, tools, _
from erppeek import Client
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


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
        help='Support Database.\n'
        'If any configured, first database will be used',
    )
    server_host = fields.Char(
        string='Server Host',
        required=True,
        help="Specified the port if port different from 80.\n"
        "For eg you can use:\n"
        "* ingadho.com\n"
        "* ingadhoc.com:8069"
    )
    contract_id = fields.Char(
        string='Contract ID',
        required=True,
        help='Remote Contract ID',
    )
    talkusID = fields.Char(
        string='Talkus ID',
        help='Remote Talkus ID',
    )
    talkus_image_url = fields.Char(string="Talkus Image URL")

    @api.multi
    def get_connection(self):
        """Function to get erpeek client"""

        self.ensure_one()
        if not self.database:
            _logger.info('No database configured, reading db list')
            db_list = self.get_client().db.list()
            if db_list:
                return self.get_client(db_list[0])
            else:
                raise Warning(_(
                    "Could not fine any database on socket '%s'") % (
                    self.server_host))
        else:
            return self.get_client(self.database)

    @api.multi
    def get_client(self, database=False):
        """You should not use this function directly, you sould call
        get_connection"""

        _logger.info('Getting client for contract %s with database %s' % (
            self.name, database))
        self.ensure_one()
        try:
            if not database:
                return Client(self.server_host)
            else:
                return Client(
                    self.server_host,
                    db=database,
                    user=self.user,
                    password=self.contract_id)
        except Exception, e:
            raise Warning(_(
                "Unable to Connect to Server. Please contact your support "
                "provider.\n"
                "This probably means that your contact is expired!\n"
                "Other possible reasons: Module 'web_support_server' is not "
                "installed or user '%s' do not exists or there is no active "
                "contract with id '%s' on database '%s'.\n\n"
                "This is what we get: %s") % (
                    self.user, self.contract_id, database, e)
            )

    @api.multi
    def check_state(self):
        self.ensure_one()
        return self.get_connection()

    @api.model
    def get_chat_values(self):
        contract = self.get_active_contract(do_not_raise=True)
        if not contract:
            return {}
        user = self.env.user
        return {
            'talkusID': contract.talkusID,
            'talkus_image_url': contract.talkus_image_url,
            'contract_id': contract.id,
            'user_id': user.id,
            'user_remote_partner_uuid': user.remote_partner_uuid,
            'user_image': user.image_small and True,
            'user_email': user.email or '',
            'user_name': user.name or '',
        }

    @api.model
    def get_active_contract(self, do_not_raise=False):
        """Funcion que permitiria incorporar estados en los contratos y
        devolver uno activo"""
        active_contract = self.search([], limit=1)
        if not active_contract:
            msg = _('No active contract configured')
            if do_not_raise:
                _logger.info(msg)
                # we return empty recordset
                return self
            else:
                raise Warning(_('No active contract configured'))
        return active_contract

    @api.multi
    def check_modules_installed(self, modules=[]):
        """
        where modules should be a list of modules names
        for eg. modules = ['database_tools']
        """
        self.ensure_one()
        client = self.get_connection()
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                return False
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
