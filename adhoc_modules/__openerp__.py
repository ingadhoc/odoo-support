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
    "name": "ADHOC Modules",
    "version": "8.0.0.1.0",
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        # we need bus to autofresh kanban view
        # 'bus',
        # module used to refresh kanban view after wizard
        'web_action_close_wizard_and_reload',
        'web_support_client',
        'database_tools',
    ],
    'external_dependencies': {
    },
    'data': [
        'views/adhoc_module_category_view.xml',
        'views/adhoc_module_view.xml',
        'views/support_view.xml',
        'views/db_configuration_view.xml',
        # 'views/templates.xml',
        'wizard/module_upgrade_view.xml',
        'wizard/base_module_pre_install_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'auto_install': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
