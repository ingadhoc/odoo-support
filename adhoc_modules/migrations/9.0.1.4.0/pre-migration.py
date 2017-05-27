# -*- coding: utf-8 -*-
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.logged_query(cr, """
        DELETE FROM ir_ui_view where model = 'db.configuration'
    """)
