import openerp.tools as tools


def get_mode():
    mode = tools.config.get('server_mode')
    if mode not in ('test', 'develop'):
        mode = False
    return mode
