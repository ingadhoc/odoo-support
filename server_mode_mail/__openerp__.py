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
    'name': 'Server Mode - Mail',
    'version': '8.0.0.0.2',
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    'license': 'AGPL-3',
    "category": "GenericModules",
    'sequence': 10,
    'description': """
Server Mode - Mail
==================
Disable send mail on mail model on develop or test environments
    """,
    'images': [],
    'depends': [
        "server_mode",
        "mail",
        ],
    'data': [
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
    'application': False,
    'qweb': [
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
