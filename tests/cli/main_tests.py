
from cement.utils import test
from boss.core import exc
from boss.cli.main import main

class CLIMainTestCase(test.CementTestCase):
    def test_main(self):
        main()

