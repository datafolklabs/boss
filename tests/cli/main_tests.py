
import os
import shutil
from boss.core import exc
from boss.cli.main import main
from boss.utils import test

@test.attr('main')
class CLIMainTestCase(test.BossTestCase):
    @test.raises(SystemExit)
    def test_main_no_args_using_sysv(self):
        main()

    def test_main_no_args(self):
        main([])

    @test.raises(exc.BossSourceError)
    def test_main_template_error(self):
        # setup the default app first to add the sources
        with self.app as app:
            app.sources.add(self.rando, self.tmp_dir, local=True)

        try:
            main(['create', '-t', 'bogus:bogus_template', self.tmp_dir])
        except exc.BossSourceError as e:
            self.eq(e.msg, "Source repo 'bogus' does not exist.")
            raise

    @test.raises(SystemExit)
    def test_main_argument_error(self):
        main(['create'])

    @test.raises(SystemExit)
    def test_main_argument_error(self):
        main(['create'])

    def test_missing_data_dir(self):
        shutil.rmtree(self.tmp_dir)
        main(['templates'])
        self.ok(os.path.exists(self.tmp_dir))

    def test_template_error(self):
        # setup the default app first to add the sources
        with self.app as app:
            app.sources.add(self.rando, self.tmp_dir, local=True)

        main(['create', '-t', '%s:bogus_template' % self.rando, self.tmp_dir])
