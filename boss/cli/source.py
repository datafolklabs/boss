
import os
import shutil
from tempfile import mkdtemp
from datetime import datetime
from cement.utils import fs, shell
from boss.cli.template import TemplateManager
from boss.core import exc

class SourceManager(object):
    def __init__(self, app):
        self.app = app

    def add(self, label, path, local=False):
        sources = self.app.db['sources']
        cache_dir = mkdtemp(dir=self.app.config.get('boss', 'cache_dir'))
        if local is True:
            path = fs.abspath(path)

        sources[label] = dict(
            label=label,
            path=path,
            cache=cache_dir,
            is_local=local,
            last_sync_time='never'
            )
        self.app.db['sources'] = sources

    def remove(self, label):
        sources = self.app.db['sources']

        if label not in sources:
            raise exc.BossSourceError("Unknown source repository.")

        cache = sources[label]['cache']
        if os.path.exists(cache):
            shutil.rmtree(cache)

        del sources[self.app.pargs.repo_label]
        self.app.db['sources'] = sources

    def sync(self, source):
        sources = self.app.db['sources']
        src = self.app.db['sources'][source]

        if not src['is_local']:
            if not os.path.exists(os.path.join(src['cache'], '.git')):
                shell.exec_cmd2([ 'git', 'clone',
                                src['path'], src['cache'] ])
            else:
                orig_dir = fs.abspath(os.curdir)
                try:
                    os.chdir(src['cache'])
                    shell.exec_cmd2(['git', 'pull'])
                    os.chdir(orig_dir)
                finally:
                    os.chdir(orig_dir)

        src['last_sync_time'] = datetime.now()
        sources[source] = src
        self.app.db['sources'] = sources

    def get_templates(self, source):
        templates = []
        src = self.app.db['sources'][source]

        if src['is_local']:
            basedir = src['path']
        else:
            basedir = src['cache']

        for entry in os.listdir(basedir):
            full_path = os.path.join(basedir, entry)
            if entry.startswith('.'):
                continue
            elif os.path.isdir(full_path):
                templates.append(entry)
        return templates

    def create_from_template(self, source, template, dest_dir):
        try:
            src = self.app.db['sources'][source]
        except KeyError as e:
            raise exc.BossTemplateError("Source repo '%s' " % source + \
                                        "does not exist.")

        if src['is_local']:
            basedir = os.path.join(src['path'], template)
        else:
            basedir = os.path.join(src['cache'], template)

        tmpl = TemplateManager(self.app, fs.abspath(basedir))
        tmpl.copy(dest_dir)
