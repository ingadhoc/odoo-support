# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import openerp.tools as tools


def get_mode():
    mode = tools.config.get('server_mode')
    # ane mode different from "empty" is considered not production
    # if mode not in ('test', 'develop', 'training', 'demo'):
    #     mode = False
    return mode
