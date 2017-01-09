# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Web Support',
    'version': '9.0.1.2.0',
    'category': 'Support',
    'sequence': 14,
    'summary': '',
    'description': """
Web Support - Client
====================
Base module for support management. Client Side.
It adds a menu under configuration where you can set up contracts (or contracts
    can be configured via infrastructure project)
    """,
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'server_mode',
        'auth_signup',
    ],
    'external_dependencies': {
        'python': ['erppeek']
    },
    'data': [
        'views/support_view.xml',
        'views/support_chat.xml',
        'views/res_users.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/web_support_client.xml',
    ],
    'demo': [
        'demo/support_contract_demo.xml',
        'demo/res_users_demo.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
