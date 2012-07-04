
import unittest
from cement.utils import test_helper as _t
from boss.cli.main import get_test_app

class CLITestCase(unittest.TestCase):
    def setUp(self):
        _t.prep()
    
    def test_cli(self):
        app = get_test_app(argv=['templates'])
        from boss.cli.bootstrap import base
        app.setup()
        app.run()
        app.close()
