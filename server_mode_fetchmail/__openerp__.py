# -*- coding: utf-8 -*-
{
    'name': 'Server Mode - Fetchmail',
    'version': '8.0.0',
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "category": "GenericModules",
    'sequence': 10,
    'description': """
Server Mode - Fetchmail
==================
Disable receive mail on Fetchmail model on develop or test environments
    """,
    'images': [],
    'depends': [
        "server_mode",
        "fetchmail",
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
