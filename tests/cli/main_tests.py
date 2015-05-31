
from cement.utils import test
from boss.core import exc
from boss.cli.main import main

class CLIMainTestCase(test.CementTestCase):
    @test.raises(SystemExit)
    def test_main_no_args(self):
        try:
            main()
        except SystemExit as e:
            self.eq(e.code, 1)
            raise

    @test.raises(SystemExit)
    def test_main_template_error(self):
        try:
            main(['create', '-t', 'bogus:bogus_template', self.tmp_dir])
        except SystemExit as e:
            self.eq(e.code, 1)
            raise

    @test.raises(SystemExit)
    def test_main_argument_error(self):
        try:
            main(['create'])
        except SystemExit as e:
            self.eq(e.code, 1)
            raise


