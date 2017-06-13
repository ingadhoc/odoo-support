# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from . import controllers

from openerp.tools import config
from openerp.addons.server_mode.mode import get_mode

# Disable crons if server mode (not production)
if get_mode():
    config['max_cron_threads'] = 0
