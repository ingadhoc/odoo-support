# -*- coding: utf-8 -*-
{
    'name': 'Web Support Issues - Client',
    'version': '1.0',
    'category': 'Support',
    'sequence': 14,
    'summary': '',
    'description': """
Web Support Issue - Client
==========================
Extends Web Support and add posibility to create issues con contract server.
Contract server requires 'project_issue_solutions' and 'infrastructure' modules.
    """,
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        'web_support_client',
        'warning_box',
    ],
    'data': [
        'wizard/support_new_issue_view.xml',
        'views/support_view.xml',
    ],
    'qweb': [
        'static/src/xml/web_support_client_issue.xml',
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
