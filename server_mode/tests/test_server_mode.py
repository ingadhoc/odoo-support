from odoo.tests.common import TransactionCase
from odoo import tools
from ..mode import get_mode


class TestServerMode(TransactionCase):

    def setUp(self):

        # if a server_module value is configured we will unset it and save the
        # old value to restore it later.
        self.old_value = tools.config.pop('server_mode')

        # NOTE: This is necessary because odoo config it does not
        # automatically rollback when the unit test ends so we need to do it
        # manually,

        super(TestServerMode, self).setUp()

    def tearDown(self, *args, **kwargs):

        # restore server mode value
        tools.config.__setitem__('server_mode', self.old_value)
        super(TestServerMode, self).tearDown()

    def test_01(self):
        """ server_mode is working properly
        """
        # server_mode is initally unset for this test.
        self.assertFalse(tools.config.get('server_mode'))

        # simulate that the server_mode param has been set.
        tools.config.__setitem__('server_mode', 'test')
        self.assertEqual(tools.config.get('server_mode'), 'test')
        self.assertEqual(get_mode(), 'test')

        # check if the ribbon is properly set with the server_mode value
        webenv = self.env['web.environment.ribbon.backend']
        ribbon_text = webenv._prepare_ribbon_name()
        self.assertEqual(ribbon_text, 'TEST')

        # check if after remove the server_mode the ribbon is properly set to
        # False.
        tools.config.pop('server_mode')
        ribbon_text = webenv._prepare_ribbon_name()
        self.assertEqual(ribbon_text, False)
