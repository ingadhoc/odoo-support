##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import odoo.tools as tools


def get_mode():
    mode = tools.config.get('server_mode')
    # NOTE: any mode different from "empty" is considered not production
    # if mode not in ('test', 'develop', 'training', 'demo'):
    #     mode = False
    return mode
