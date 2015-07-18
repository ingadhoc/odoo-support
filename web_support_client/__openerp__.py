# -*- coding: utf-8 -*-
{
    'name': 'Web Support',
    'version': '1.0',
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
    'author':  'ADHOC SA',
    'website': 'www.ingadhoc.com',
    'images': [
    ],
    'depends': [
        'base',
    ],
    'data': [
        'views/support_view.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/web_support_client.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
