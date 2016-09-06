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
    'name': 'Server Mode',
    'version': '8.0.0.2.0',
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    'license': 'AGPL-3',
    "category": "GenericModules",
    'sequence': 10,
    'description': """
Server Mode
===========
This modules disable some functions when running databases on odoo servers with
parameter server_mode = "some value"
This module is also inherited by other modules so that you can disable
functionalities depending on server mode. To use it:
* import with: from openerp.addons.server_mode.mode import get_mode
* use it like following:
    * if mode() == 'test':
    * if mode() == 'develop'
    * if mode():
    ... etc

    """,
    'images': [],
    'depends': [
        "web",
        ],
    'data': [
        "oerp_develope_js.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
    'application': False,
    'qweb': [
        'static/src/xml/mode.xml',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
