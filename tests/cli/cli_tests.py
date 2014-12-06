
import os
import sys
import shutil
from tempfile import mkdtemp
from cement.core import backend
from cement.utils import test, shell
import boss
from boss.cli.main import get_test_app
from boss.core import exc

class CLITestCase(test.CementTestCase):
    ### FIX ME: This should be a remote.. but is a failed process... using
    ### local
    def test_00_add_source(self):
        app = get_test_app(
            argv=['add-source', 'test', './tests/templates', '--local'])
        app.setup()
        app.run()
        app.close()

    def test_01_add_local_source(self):
        # get real sources for our local source
        app = get_test_app(argv=['sources'])
        app.setup()
        app.run()
        local = app.db['sources']['test']['cache']
        app.close()

        app = get_test_app(argv=['add-source', 'test-local', local,
                                 '--local'])
        app.setup()
        app.run()
        app.close()

    @test.raises(exc.BossArgumentError)
    def test_add_source_bad_arguments(self):
        try:
            app = get_test_app(argv=['add-source'])
            app.setup()
            app.run()
        except exc.BossArgumentError as e:
            self.eq(e.msg, "Repository name and path required.")
            raise
        finally:
            app.close()

    def test_01_sync(self):
        app = get_test_app(argv=['sync'])
        app.setup()
        app.run()
        app.close()

        # sync again for coverage
        app = get_test_app(argv=['sync'])
        app.setup()
        app.run()
        app.close()

    def test_list_sources(self):
        app = get_test_app(argv=['sources'])
        app.setup()
        app.run()
        app.close()

    def test_list_templates(self):
        app = get_test_app(argv=['templates'])
        app.setup()
        app.run()
        app.close()

    @test.raises(exc.BossArgumentError)
    def test_default(self):
        try:
            app = get_test_app(argv=[''])
            app.setup()
            app.run()
        finally:
            app.close()

    @test.raises(exc.BossArgumentError)
    def test_create_bad_destination(self):
        try:
            app = get_test_app(argv=['create'])
            app.setup()
            app.run()
        except exc.BossArgumentError as e:
            test.eq(e.msg, "Destination path required.")
            raise
        finally:
            app.close()

    @test.raises(exc.BossArgumentError)
    def test_create_missing_template(self):
        try:
            app = get_test_app(argv=['create', self.tmp_dir])
            app.setup()
            app.run()
        except exc.BossArgumentError as e:
            test.eq(e.msg, "Template label required.")
            raise
        finally:
            app.close()

    # def test_create(self):
    #     try:
    #         answers = dict(
    #             version='0.9.1',
    #             module='test_python_module',
    #             project='Test Pyton Project',
    #             description='Project Description',
    #             creator='Project Creator',
    #             email='nobody@example.com',
    #             license='BSD',
    #             url='http://project.example.com',
    #             )
    #         app = get_test_app(
    #             argv=[
    #                 'create',
    #                 '%s/dest' % self.tmp_dir,
    #                 '-t',
    #                 'test:python',
    #                 '--defaults',
    #                 ],
    #             )
    #         app.setup()
    #         app.config.merge(dict(answers=answers))
    #         app.run()
    #     finally:
    #         app.close()

    def test_create_from_local_source(self):
        try:
            answers = dict(
                version='0.9.1',
                module='test_python_module',
                project='Test Pyton Project',
                description='Project Description',
                creator='Project Creator',
                email='nobody@example.com',
                license='BSD',
                url='http://project.example.com',
                )
            app = get_test_app(
                argv=[
                    'create',
                    '%s/dest' % self.tmp_dir,
                    '-t',
                    'test:python',
                    '--defaults',
                    ],
                )
            app.setup()
            app.config.merge(dict(answers=answers))
            app.run()
        finally:
            app.close()

    def test_create_default_source(self):
        try:
            answers = dict(
                version='0.9.1',
                module='test_python_module',
                project='Test Pyton Project',
                description='Project Description',
                creator='Project Creator',
                email='nobody@example.com',
                license='BSD',
                url='http://project.example.com',
                )
            app = get_test_app(
                argv=[
                    'create',
                    '%s/dest' % self.tmp_dir,
                    '-t',
                    'python',
                    '--defaults',
                    ],
                )
            app.setup()
            app.config.merge(dict(answers=answers))
            app.run()
        finally:
            app.close()

    def test_cli(self):
        app = get_test_app(argv=['templates'])
        app.setup()
        app.run()
        app.close()

    def test_rm_source(self):
        app = get_test_app(argv=['rm-source', 'test'])
        app.setup()
        app.run()
        app.close()

    @test.raises(exc.BossArgumentError)
    def test_rm_source_no_label(self):
        try:
            app = get_test_app(argv=['rm-source'])
            app.setup()
            app.run()
            app.close()
        except exc.BossArgumentError as e:
            self.eq(e.msg, "Repository name required.")
            raise
        finally:
            app.close()

    @test.raises(exc.BossArgumentError)
    def test_rm_source_bad_label(self):
        try:
            app = get_test_app(argv=['rm-source', 'test-bogus'])
            app.setup()
            app.run()
        except exc.BossArgumentError as e:
            self.eq(e.msg, "Unknown source repository.")
            raise
        finally:
            app.close()

    def test_clean(self):
        os.system('touch %s/test_file.boss.bak' % self.tmp_dir)
        app = get_test_app(argv=['clean', self.tmp_dir])
        app.setup()
        app.run()
        app.close()

        self.eq(os.path.exists('%s/test_file.boss.bak' % self.tmp_dir), False)

    @test.raises(exc.BossArgumentError)
    def test_clean_missing_project(self):
        try:
            app = get_test_app(argv=['clean'])
            app.setup()
            app.run()
        except exc.BossArgumentError as e:
            self.eq(e.msg, "Project path required.")
            raise
        finally:
            app.close()


    def test_zz_missing_data_dir(self):
        app = get_test_app(argv=['templates'])
        app.setup()
        shutil.rmtree(app.config.get('boss', 'data_dir'))
        app.validate_config()
        app.close()


