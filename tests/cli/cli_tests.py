
import sys
import shutil
from cement.core import backend
from cement.utils import test
import boss
from boss.cli.main import get_test_app
    
class CLITestCase(test.CementTestCase):
    def test_cli(self):
        app = get_test_app(argv=['templates'])
        app.setup()
        app.run()
        app.close()

    def test_missing_data_dir(self):
        app = get_test_app(argv=['templates'])
        app.setup()
        shutil.rmtree(app.config.get('boss', 'data_dir'))
        app.validate_config()
    
    def test_sync(self):
        app = get_test_app(argv=['sync'])
        app.setup()
        app.run()
        app.close()
        

    