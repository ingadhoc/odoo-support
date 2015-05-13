# -*- coding: utf-8 -*-
{
    "name": "Database Tools",
    "version": "1.0",
    'author':  'ADHOC SA',
    'website': 'www.ingadhoc.com',
    # "category": "Accounting",
    "description": """
Database Tools
==============
TODO
    """,
    'depends': [
        'base'
        ],
    'data': [
        'views/database_backup_view.xml',
        'views/database_preserve_view.xml',
        'views/database_view.xml',
        'security/ir.model.access.csv',
        'data/backups_preserve_rules_data.xml',
        'data/backup_data.xml',
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'auto_install': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
