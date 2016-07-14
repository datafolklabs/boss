
import os
import sys
import shutil
import re
from tempfile import mkdtemp
from cement.ext.ext_argparse import ArgparseController, expose
from cement.utils import fs
from boss.utils.version import get_version
from boss.core import exc as boss_exc

VERSION = get_version()
BANNER = """

  _______  _______ _______ _______
 |   _   \|   _   |   _   |   _   |
 |.  1   /|.  |   |   1___|   1___|
 |.  _   \|.  |   |____   |____   |
 |:  1    |:  1   |:  1   |:  1   |
 |::.. .  |::.. . |::.. . |::.. . |
 `-------'`-------`-------`-------'
 Copyright (c) 2015 Data Folk Labs, LLC
 Version %s


""" % VERSION

class BossBaseController(ArgparseController):
    class Meta:
        label = 'base'
        description = 'Boss Templates and Development Utilities'
        arguments = [
            # (['-t', '--template'],
            #  dict(help="a template label", dest='template')),
            # (['--local'],
            #  dict(help='toggle a local source repository',
            #       action='store_true', default=False)),
            (['--version'], dict(action='version', version=BANNER)),
            # (['--defaults'],
            #  dict(action='store_true',
            #       help='use default answers without prompting')),
            # (['extra'],
            #  dict(help='additional positional arguments',
            #       action='store', nargs='*')),
            ]

    @expose(hide=True)
    def default(self):
        raise boss_exc.BossArgumentError("A sub-command is required.  "
                                         "Please see --help.")

    # ------------------------------------------------------------------------
    @expose(
        help="create project files from a template",
        arguments=[
            (['-t', '--template'],
             dict(help="a template label", dest='template')),
            (['--defaults'],
             dict(action='store_true',
                  help='use default answers without prompting')),
            (['project_path'],
             dict(help='project destination path', action='store')),
        ]
    )
    def create(self):
        if not len(self.app.pargs.project_path) >= 1:
            raise boss_exc.BossArgumentError("Destination path required.")

        if not self.app.pargs.template:
            raise boss_exc.BossArgumentError("Template label required.")

        sources = self.app.db.get('sources')

        try:
            tmpl_parts = self.app.pargs.template.split(':')
            source = tmpl_parts[0]
            template = tmpl_parts[1]
        except IndexError as e:
            source = 'boss'
            template = self.app.pargs.template

        #src = SourceManager(self.app)
        self.app.sources.create_from_template(source, template, 
                                              self.app.pargs.project_path)

    # ------------------------------------------------------------------------
    @expose(help="list all available templates")
    def templates(self):
        print('')
        sources = self.app.db['sources']
        for label,data in sources.items():
            print("Source: %s" % label)
            print('-' * 78)
            if data['is_local'] is True:
                local_path = sources[label]
                remote_path = None
            else:
                local_path = "%s/templates/%s" % (
                            self.app.config.get('boss', 'data_dir'), label,
                            )
                remote_path = sources[label]

            #src = SourceManager(self.app)
            for tmpl in self.app.sources.get_templates(label):
                print(tmpl)

            print('')

    # ------------------------------------------------------------------------
    @expose(help="sync a source repository")
    def sync(self):
        _sources = self.app.db['sources']
        for label in self.app.db['sources']:
            print("Syncing %s Templates . . . " % label.capitalize())
            #src = SourceManager(self.app)
            self.app.sources.sync(label)
            print('')

    # ------------------------------------------------------------------------
    @expose(help="list template source repositories")
    def sources(self):
        for key in self.app.db['sources']:
            src = self.app.db['sources'][key]
            print('')
            print("--        Label: %s" % src['label'])
            print("    Source Path: %s" % src['path'])
            print("          Cache: %s" % src['cache'])
            print("     Local Only: %s" % src['is_local'])
            print(" Last Sync Time: %s" % src['last_sync_time'])
        print('')

    # ------------------------------------------------------------------------
    @expose(
        help="add a template source repository",
        arguments=[
            (['--local'],
             dict(help='toggle a local source repository',
                  action='store_true', default=False, dest='local')),
            (['repo_label'],
             dict(help='repository label identifier', action='store')),
            (['repo_path'],
             dict(help='repository path', action='store')),
        ]
    )
    def add_source(self):
        label = self.app.pargs.repo_label
        path = self.app.pargs.repo_path
        self.app.sources.add(label, path, local=self.app.pargs.local)
    
    # ------------------------------------------------------------------------
    @expose(
        help="remove a source repository",
        arguments=[
            (['repo_label'],
             dict(help='repository label identifier', action='store')),
        ]
    )
    def rm_source(self):
        self.app.sources.remove(self.app.pargs.repo_label)

    # ------------------------------------------------------------------------
    @expose(
        help="remove .boss.bak* files from path",
        arguments=[
            (['project_path'],
             dict(help='project destination path', action='store')),
        ]
    )
    def clean(self):
        for items in os.walk(self.app.pargs.project_path):
            for _file in items[2]:
                path = fs.abspath(os.path.join(items[0], _file))
                if re.match('(.*)\.boss\.bak(.*)', path):
                    self.app.log.warn("Removing: %s" % _file)
                    os.remove(path)


