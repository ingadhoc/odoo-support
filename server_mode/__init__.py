##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from odoo.tools import config
from .mode import get_mode

from . import models

# Disable crons if server mode (not production)
if get_mode():
    config['max_cron_threads'] = 0
