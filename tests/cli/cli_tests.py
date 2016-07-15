
import os
import sys
import shutil
from tempfile import mkdtemp
from cement.core import backend
from cement.utils import shell
import boss
from boss.core import exc
from boss.utils import test

@test.attr('cli')
class CLITestCase(test.BossTestCase):
    ### FIX ME: This should be a remote.. but is a failed process... using
    ### local
    def test_add_source(self):
        argv = ['add-source', self.rando, self.tmp_dir]
        with self.make_app(argv=argv) as app:
            app.run()

            res = self.rando in app.db['sources'].keys()
            self.ok(res)

            self.eq(app.db['sources'][self.rando]['is_local'], False)

    def test_add_local_source(self):
        argv = ['add-source', '--local', self.rando, self.tmp_dir]
        with self.make_app(argv=argv) as app:
            app.run()

            res = self.rando in app.db['sources'].keys()
            self.ok(res)

            self.eq(app.db['sources'][self.rando]['is_local'], True)

    def test_sync(self):
        # setup the default app first to add the sources
        with self.app as app:
            app.sources.add(self.rando, self.tmp_dir, local=True)

        argv = ['sync']
        with self.make_app(argv=argv) as app:
            app.run()

        # sync again for coverage
        with self.make_app(argv=argv) as app:
            app.run()

    def test_list_sources(self):
        # setup the default app first to add the sources
        with self.app as app:
            app.sources.add(self.rando, self.tmp_dir, local=True)

        argv = ['sources']
        with self.make_app(argv=argv) as app:
            app.run()

    def test_rm_source(self):
        # setup the default app first to add the sources
        with self.app as app:
            app.sources.add(self.rando, self.tmp_dir, local=True)

        argv = ['rm-source', self.rando]
        with self.make_app(argv=argv) as app:
            app.run()

            res = self.rando not in app.db['sources'].keys()
            self.ok(res)

    @test.raises(exc.BossSourceError)
    def test_rm_source_unknown_repo(self):
        # setup the default app first to add the sources
        with self.app as app:
            app.sources.add(self.rando, self.tmp_dir, local=True)

        argv = ['rm-source', 'some-unknown-repo']
        with self.make_app(argv=argv) as app:
            try:
                app.run()
            except exc.BossSourceError as e:
                self.eq(e.msg, "Unknown source repository.")
                raise

    def test_list_templates(self):
        # setup the default app first to add the sources
        with self.app as app:
            app.sources.add(self.rando, self.tmp_dir, local=True)

        # add a hidden dir for coverage
        os.makedirs(os.path.join(self.tmp_dir, '.boss.test'))

        argv = ['templates']
        with self.make_app(argv=argv) as app:
            app.run()

    def test_create(self):
        # setup the default app first to add the sources
        with self.app as app:
            # create a fake template
            data_dir = self.app.config.get('boss', 'data_dir')
            os.makedirs(os.path.join(data_dir, self.rando))
            f = open(os.path.join(data_dir, self.rando, 'boss.yml'), 'w')
            f.write("fake: yaml")
            f.close()
            app.sources.add(self.rando, self.tmp_dir, local=True) 
            app.sources.sync(self.rando)

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

        argv=[
            'create',
            '--defaults',
            '-t',
            '%s:%s' % (self.rando, self.rando),
            '%s/dest' % self.tmp_dir,
        ]
        with self.make_app(argv=argv) as app:
            app.config.merge(dict(answers=answers))
            app.run()

    def test_create_from_non_local(self):
        # setup the default app first to add the sources and a fake template
        with self.app as app:
            app.sources.sync('boss')

            data_dir = app.db['sources']['boss']['cache']
            os.makedirs(os.path.join(data_dir, self.rando))
            f = open(os.path.join(data_dir, self.rando, 'boss.yml'), 'w')
            f.write("fake: yaml")
            f.close()
            

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

        argv=[
            'create',
            '-t',
            'boss:%s' % self.rando,
            '%s/dest' % self.tmp_dir,
        ]
        with self.make_app(argv=argv) as app:
            app.run()

    def test_create_default_source(self):
        # setup the default app first to add the sources
        with self.app as app:
            # create a fake template
            data_dir = self.app.config.get('boss', 'data_dir')
            os.makedirs(os.path.join(data_dir, self.rando))
            f = open(os.path.join(data_dir, self.rando, 'boss.yml'), 'w')
            f.write("fake: yaml")
            f.close()
            app.sources.add('boss', self.tmp_dir, local=True)    
            app.sources.sync('boss')

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

        argv=[
            'create',
            '--defaults',
            '-t',
            self.rando,
            '%s/dest' % self.tmp_dir,
        ]
        with self.make_app(argv=argv) as app:
            app.run()

    def test_clean(self):
        f = open(os.path.join(self.tmp_dir, "%s.boss.bak" % self.rando), 'w')
        f.write(self.rando)
        f.close() 

        argv=['clean', self.tmp_dir]
        with self.make_app(argv=argv) as app:
            app.run()

        self.eq(os.path.exists('%s/test_file.boss.bak' % self.tmp_dir), False)

    # def test_create_from_local_source(self):
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

    # def test_create_default_source(self):
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
    #                 'python',
    #                 '--defaults',
    #                 ],
    #             )
    #         app.setup()
    #         app.config.merge(dict(answers=answers))
    #         app.run()
    #     finally:
    #         app.close()

    # def test_cli(self):
    #     app = get_test_app(argv=['templates'])
    #     app.setup()
    #     app.run()
    #     app.close()

    # def test_rm_source(self):
    #     app = get_test_app(argv=['rm-source', 'test'])
    #     app.setup()
    #     app.run()
    #     app.close()

    # @test.raises(exc.BossArgumentError)
    # def test_rm_source_bad_label(self):
    #     try:
    #         app = get_test_app(argv=['rm-source', 'test-bogus'])
    #         app.setup()
    #         app.run()
    #     except exc.BossArgumentError as e:
    #         self.eq(e.msg, "Unknown source repository.")
    #         raise
    #     finally:
    #         app.close()

    # def test_clean(self):
    #     os.system('touch %s/test_file.boss.bak' % self.tmp_dir)
    #     app = get_test_app(argv=['clean', self.tmp_dir])
    #     app.setup()
    #     app.run()
    #     app.close()

    #     self.eq(os.path.exists('%s/test_file.boss.bak' % self.tmp_dir), False)

    # @test.raises(exc.BossArgumentError)
    # def test_clean_missing_project(self):
    #     try:
    #         app = get_test_app(argv=['clean'])
    #         app.setup()
    #         app.run()
    #     except exc.BossArgumentError as e:
    #         self.eq(e.msg, "Project path required.")
    #         raise
    #     finally:
    #         app.close()


    # def test_zz_missing_data_dir(self):
    #     app = get_test_app(argv=['templates'])
    #     app.setup()
    #     shutil.rmtree(app.config.get('boss', 'data_dir'))
    #     app.validate_config()
    #     app.close()


