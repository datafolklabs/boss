
import os
from datetime import datetime
from cement.utils import fs, shell
from boss.cli.template import TemplateManager

class SourceManager(object):
    def __init__(self, app):
        self.app = app

    def sync(self, source):
        sources = self.app.db['sources']
        src = self.app.db['sources'][source]
        if not src['is_local']:
            if not os.path.exists(os.path.join(src['cache'], '.git')):
                shell.exec_cmd2([ 'git', 'clone',
                                src['path'], src['cache'] ])
            else:
                os.chdir(src['cache'])
                shell.exec_cmd2(['git', 'pull'])
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
        src = self.app.db['sources'][source]
        if src['is_local']:
            basedir = os.path.join(src['path'], template)
        else:
            basedir = os.path.join(src['cache'], template)

        tmpl = TemplateManager(self.app, fs.abspath(basedir))
        tmpl.copy(dest_dir)
