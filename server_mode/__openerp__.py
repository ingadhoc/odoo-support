# -*- coding: utf-8 -*-
{
    'name': 'Server Mode',
    'version': '7.0.0',
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "category": "GenericModules",
    'sequence': 10,
    'description': """
Server Mode
===========
This modules disable some functions when running databases on odoo servers with
parameter server_mode = test or server_mode = develop.
This module is also inherited by other modules so that you can disable
functionalities depending on server mode. To use it:
* import with: from openerp.addons.server_mode.mode import get_mode
* use it like following:
    * if mode() == 'test':
    * if mode() == 'develop'
    * if mode():

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
