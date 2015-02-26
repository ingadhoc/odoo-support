{
    'name' : 'Odoo Live Support',
    'author': 'OpenERP SA',
    'version': '1.0',
    'summary': 'Chat with the Odoo collaborators',
    'category': 'Tools',
    'complexity': 'medium',
    'website': 'https://www.odoo.com/',
    'description':
        """
Odoo Live Support
=================

Ask your functionnal question directly to the Odoo Operators with the livechat support.

        """,
    'data': [
        "views/im_odoo_support.xml"
    ],
    'depends' : ["web_support_client", "im_chat"],
    'qweb': [
        'static/src/xml/im_odoo_support.xml'
    ],
    'installable': False,
    'auto_install': True,
    'application': True,
}
