# -*- coding: utf-8 -*-
{
    'name': 'Web Support Issue - Server',
    'version': '1.0',
    'category': 'Support',
    'sequence': 14,
    'summary': '',
    'description': """
Web Support Issue - Server
==========================
Gives possibility to web support clients to load issues
    """,
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'images': [
    ],
    'depends': [
        'web_support_server',
        # modulo requerido por algunos campos adicionales en los issues
        'infrastructure_contract',
        # modulo requerido para que web support client pueda cargar incidencias
        'project_issue_solutions',
    ],
    'data': [
        'security/ir.model.access.csv',
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
