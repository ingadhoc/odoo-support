# -*- coding: utf-8 -*-
{
    'name': 'Web Support Website Doc - Client',
    'version': '1.0',
    'category': 'Support',
    'sequence': 14,
    'summary': '',
    'description': """
Web Support Client with Website Documentation Integration
=========================================================
    """,
    'author':  'ADHOC SA',
    'website': 'www.ingadhoc.com',
    'images': [
    ],
    'depends': [
        'web_support_client',
        'website_doc',
    ],
    'data': [
        'views/support_view.xml',
        'data/cron.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
