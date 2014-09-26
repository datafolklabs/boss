
from cement.utils import test
from boss.core import exc
from boss.cli.main import main

class CLIMainTestCase(test.CementTestCase):
    def test_main_no_args(self):
        main()

    def test_main_template_error(self):
        main(['create', '-t', 'bogus:bogus_template', self.tmp_dir])

    def test_main_argument_error(self):
        main(['create'])


