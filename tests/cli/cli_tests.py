
import sys
import shutil
import unittest
from cement.core import backend
from cement.utils import test_helper as _t
import boss
from boss.cli.main import get_test_app

if sys.version_info[0] >= 3:
    from imp import reload
    
class CLITestCase(unittest.TestCase):
    def setUp(self):
        _t.prep()
    
    def test_cli(self):
        app = get_test_app(argv=['templates'])
        import boss.cli.bootstrap.base
        app.setup()
        app.run()
        app.close()

    def test_missing_data_dir(self):
        app = get_test_app(argv=['templates'])
        reload(boss.cli.bootstrap.base)
        app.setup()
        shutil.rmtree(app.config.get('boss', 'data_dir'))
        app.validate_config()
