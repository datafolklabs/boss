
import os
import sys
import shutil
import shelve
import json
import re
from tempfile import mkdtemp
from datetime import datetime
from cement.core.controller import CementBaseController, expose
from cement.utils import fs, shell
from boss import VERSION
from boss.core import exc as boss_exc

if sys.version_info[0] < 3:
    from urllib2 import urlopen, HTTPError # pragma: no cover
else:
    from urllib.request import urlopen, HTTPError # pragma: no cover


BANNER = """

  _______  _______ _______ _______
 |   _   \|   _   |   _   |   _   |
 |.  1   /|.  |   |   1___|   1___|
 |.  _   \|.  |   |____   |____   |
 |:  1    |:  1   |:  1   |:  1   |
 |::.. .  |::.. . |::.. . |::.. . |
 `-------'`-------`-------`-------'
      (c) 2014 Data Folk Labs, LLC
                           v%s

""" % VERSION

ALLOWED_STR_METHODS = [
    'upper',
    'lower',
    'title',
    'swapcase',
    'strip',
    'capitalize'
]

class Template(object):
    def __init__(self, app, path):
        self.app = app
        self.basedir = fs.abspath(path)
        self.config = self._get_config()
        self._word_map = dict()
        self._vars = dict()

    def _get_config(self):
        config = None
        possibles = [
            fs.abspath(os.path.join(self.basedir, 'boss.json')),
            fs.abspath(os.path.join(self.basedir, 'boss.yml')),
            ]
        for path in possibles:
            if os.path.exists(path):
                if os.path.basename(path) == 'boss.json':
                    config = self._get_json_config(path)
                    break
                elif os.path.basename(path) == 'boss.yml':
                    config = self._get_yaml_config(path)
                    break

        if not config:
            raise boss_exc.BossTemplateError("No supported config found.")

        # fix it up with some defaults
        if 'delimiter' not in config.keys():
            config['delimiter'] = '@'

        return config

    def _get_json_config(self, path):
        full_path = fs.abspath(path)
        if not os.path.exists(full_path):
            raise boss_exc.BossTemplateError("Invalid template config.")

        self.app.log.debug('loading template config %s' % full_path)

        import json
        return json.load(open(full_path, 'r'))

    def _get_yaml_config(self, path):
        full_path = fs.abspath(path)
        if not os.path.exists(full_path):
            raise boss_exc.BossTemplateError("Invalid template config.")

        self.app.log.debug('loading template config %s' % full_path)

        try:
            import yaml
        except ImportError as e:
            raise boss_exc.BossRuntimeError("Unable to import yaml.  " +
                                            "Please install pyYaml.")

        return yaml.load(open(full_path, 'r'))

    def _populate_vars(self):
        if 'variables' in self.config.keys():
            for var,question in self.config['variables'].items():
                if var.lower() in self.app.config.keys('answers'):
                    default = self.app.config.get('answers', var.lower())
                    res = raw_input("%s: [%s] " % (question, default))
                    if len(res) == 0:
                        res = default
                else:
                    res = raw_input("%s: " % question)
                self._vars[var] = res.strip()

    def _sub(self, txt):
        ### FIX ME: This needs serious refactoring... PLEASE

        # do per item substitution rather than entire txt to avoid variable
        # confusion.  Also allows us to call .capitalize, .lower, etc on the
        # string after substitution.
        for line in str(txt).split('\n'):
            for item in line.split(' '):
                # Not a template var? (generic pattern)
                pattern = "(.*)\%s(.*)\%s(.*)" % \
                    (self.config['delimiter'], self.config['delimiter'])

                if not re.match(pattern, item):
                    continue

                for key,value in sorted(self._vars.items()):
                    if key in self._word_map:
                        continue

                    pattern = "(.*)\%s(%s)\%s(.*)" % (
                        self.config['delimiter'],
                        key,
                        self.config['delimiter'],
                        )

                    m = re.match(pattern, item)
                    if m:
                        map_key = "%s%s%s" % (
                            self.config['delimiter'],
                            m.group(2),
                            self.config['delimiter'],
                            )
                        self._word_map[map_key] = str(value)
                    else:
                        pattern = "(.*)\%s(%s)\.([_a-z0-9]*)\%s(.*)" % (
                            self.config['delimiter'],
                            key,
                            self.config['delimiter'],
                            )
                        m = re.match(pattern, item)
                        if m:
                            # string method calls?
                            if len(m.group(3)) > 0:
                                if m.group(3) in ALLOWED_STR_METHODS:
                                    fixed = str(getattr(value, m.group(3))())
                                else:
                                    self.app.log.debug("str method '%s' not allowed." % m.group(3))
                                    fixed = str(value)
                            else:
                                fixed = str(value)

                            new_key = "%s%s.%s%s" % (
                                self.config['delimiter'],
                                m.group(2),
                                m.group(3),
                                self.config['delimiter'],
                                )
                            self._word_map[new_key] = fixed

        # actually replace the text
        new_txt = txt
        for pattern,replacement in sorted(self._word_map.items()):
            new_txt = re.sub(pattern, replacement, new_txt)

        return new_txt

    def _sub_or_pass(self, path, data):
        if 'excludes' in self.config.keys():
            for pattern in self.config['excludes']:
                if re.match(pattern, path):
                    self.app.log.debug(
                        "not doing substitutions for excluded %s" % path
                        )
                    # don't do subs
                    return data
        return self._sub(data)

    def _inject(self, dest_path):
        new_data = ''
        write_it = False

        f = open(dest_path, 'r')
        line_num = 0
        for line in f.readlines():
            line_num = line_num + 1
            # only one injection per line is allowed
            for inj,inj_data in self.config['injections'].items():
                pattern = '(.*)\%sboss.mark\:%s\%s(.*)' % (
                    self.config['delimiter'],
                    inj,
                    self.config['delimiter'],
                    )
                m = re.match(pattern, line)
                if m:
                    print("Injecting %s into %s at line #%s" % \
                         (inj, dest_path, line_num))
                    line = line + "%s\n" % self._sub(inj_data)
                    write_it = True
                    break

            new_data = new_data + line
        f.close()

        if write_it:
            fs.backup(dest_path, suffix='.boss.bak')
            self._write_file(dest_path, new_data, overwrite=True)

    def _inject_or_pass(self, path):
        if 'excludes' in self.config.keys():
            for pattern in self.config['excludes']:
                if re.match(pattern, path):
                    self.app.log.debug(
                        "not doing injections for excluded %s" % path
                        )
                    return False
        return self._inject(path)
        return True

    def _copy_path(self, tmpl_path, dest_path):
        f = open(fs.abspath(tmpl_path), 'r')
        data = f.read()
        f.close()

        dest_path = self._sub(fs.abspath(dest_path))
        dest_data = self._sub_or_pass(tmpl_path, data)
        self._write_file(dest_path, dest_data)

    def _write_file(self, dest_path, data, overwrite=False):
        if os.path.exists(dest_path) and overwrite == False:
            self.app.log.warn('File Exists: %s' % dest_path)
            return False

        self.app.log.info('Writing: %s' % dest_path)
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))
        f = open(dest_path, 'w')
        f.write(data)
        f.close()
        return True

    def _walk_path(self, path):
        for items in os.walk(fs.abspath(path)):
            for _file in items[2]:
                if _file == 'boss.yml':
                    continue
                elif re.match('(.*)\.boss\.bak(.*)', _file):
                    continue
                else:
                    yield fs.abspath(os.path.join(items[0], _file))

    def copy(self, dest_basedir):
        self._populate_vars()
        dest_basedir = fs.abspath(dest_basedir)

        # first handle local files
        for tmpl_path in self._walk_path(self.basedir):
            dest_path = fs.abspath(re.sub(self.basedir, dest_basedir, tmpl_path))
            self._copy_path(tmpl_path, dest_path)

        # second handle external files
        if 'external_files' in self.config.keys():
            for _file, remote_uri in self.config['external_files'].items():
                dest_path = self._sub(os.path.join(dest_basedir, _file))
                remote_uri = self._sub(remote_uri)
                try:
                    data = self._sub(urlopen(remote_uri).read())
                except HTTPError as e:
                    data = ''

                self._write_file(dest_path, data)

        # lastly do injections
        if 'injections' in self.config.keys() \
            and len(self.config['injections']) > 0:
            for dest_path in self._walk_path(dest_basedir):
                self._inject_or_pass(dest_path)


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

        tmpl = Template(self.app, fs.abspath(basedir))
        tmpl.copy(dest_dir)

class BossBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'Boss Templates and Development Utilities'
        arguments = [
            (['-t', '--template'],
             dict(help="a template label", dest='template')),
            (['--local'],
             dict(help='toggle a local source repository',
                  action='store_true', default=False)),
            (['--version'], dict(action='version', version=BANNER)),
            (['modifier1'], dict(help='command modifier', nargs='?')),
            (['modifier2'], dict(help='command modifier', nargs='?')),
            ]
        config_defaults = dict()

    @expose(hide=True)
    def default(self):
        print("A sub-command is required.  Please see --help.")
        sys.exit(1)

    @expose(help="create project files from a template")
    def create(self):
        if not self.app.pargs.modifier1:
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

        src = SourceManager(self.app)
        src.create_from_template(source, template, self.app.pargs.modifier1)

    @expose(help="list all available templates")
    def templates(self):
        print('')
        sources = self.app.db['sources']
        for label in sources:
            print("%s Templates" % label.capitalize())
            print('-' * 78)
            if label == 'local':
                local_path = sources[label]
                remote_path = None
            else:
                local_path = "%s/templates/%s" % (
                            self.app.config.get('boss', 'data_dir'), label,
                            )
                remote_path = sources[label]

            src = SourceManager(self.app)
            for tmpl in src.get_templates(label):
                print(tmpl)

            print('')

    @expose(help="sync a source repository")
    def sync(self):
        _sources = self.app.db['sources']
        for label in self.app.db['sources']:
            print("Syncing %s Templates . . . " % label.capitalize())
            src = SourceManager(self.app)
            src.sync(label)
            print('')

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

    @expose(help="add a template source repository")
    def add_source(self):
        if not self.app.pargs.modifier1 or not self.app.pargs.modifier2:
            raise boss_exc.BossArgumentError("Repository name and path required.")

        sources = self.app.db['sources']
        label = self.app.pargs.modifier1
        path = self.app.pargs.modifier2
        cache_dir = mkdtemp(dir=self.app.config.get('boss', 'cache_dir'))

        if self.app.pargs.local:
            path = fs.abspath(path)

        sources[label] = dict(
            label=label,
            path=path,
            cache=cache_dir,
            is_local=self.app.pargs.local,
            last_sync_time='never'
            )
        self.app.db['sources'] = sources

    @expose(help="remove a source repository")
    def rm_source(self):
        sources = self.app.db['sources']

        if not self.app.pargs.modifier1:
            raise boss_exc.BossArgumentError("Repository name required.")
        elif self.app.pargs.modifier1 not in sources:
            raise boss_exc.BossArgumentError("Unknown source repository.")

        cache = sources[self.app.pargs.modifier1]['cache']
        if os.path.exists(cache):
            shutil.rmtree(cache)

        del sources[self.app.pargs.modifier1]
        self.app.db['sources'] = sources

    @expose(help="remove .boss.bak* files from path")
    def clean(self):
        if not self.app.pargs.modifier1:
            raise boss_exc.BossArgumentError("Project path required.")
        for items in os.walk(self.app.pargs.modifier1):
            for _file in items[2]:
                path = fs.abspath(os.path.join(items[0], _file))
                if re.match('(.*)\.boss\.bak(.*)', path):
                    self.app.log.warn("Removing: %s" % _file)
                    os.remove(path)


