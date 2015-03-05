
import os
import sys
import re
import json
from cement.utils import fs
from boss.core import exc as boss_exc

if sys.version_info[0] < 3:
    from urllib2 import urlopen, HTTPError      # pragma: no cover
    from ConfigParser import RawConfigParser    # pragma: no cover
    input = raw_input                           # pragma: no cover
else:
    from urllib.request import urlopen, HTTPError # pragma: no cover
    from configparser import RawConfigParser  # pragma: no cover

ALLOWED_STR_METHODS = [
    'upper',
    'lower',
    'title',
    'swapcase',
    'strip',
    'capitalize'
]

class TemplateManager(object):
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
        if 'delimiters' not in config.keys():
            config['delimiters'] = ('@', '@')
            config['start_delimiter'] = config['delimiters'][0]
            config['end_delimiter'] = config['delimiters'][1]
        else:
            config['start_delimiter'] = config['delimiters'][0]
            config['end_delimiter'] = config['delimiters'][1]

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
                if self.app.pargs.defaults is True:
                    try:
                        res = self.app.config.get('answers', var)
                    except ConfigParser.NoOptionError as e:
                        res = "MISSING VARIABLE"
                else:
                    if var.lower() in self.app.config.keys('answers'):
                        default = self.app.config.get('answers', var.lower())
                        res = input("%s: [%s] " % (question, default))
                        if len(res) == 0:
                            res = default
                    else:
                        res = input("%s: " % question)
                self._vars[var] = res.strip()

    def _sub(self, txt):
        ### FIX ME: This needs serious refactoring... PLEASE

        # do per item substitution rather than entire txt to avoid variable
        # confusion.  Also allows us to call .capitalize, .lower, etc on the
        # string after substitution.
        for line in str(txt).split('\n'):
            for item in line.split(' '):
                # Not a template var? (generic pattern)
                pattern = "(.*)\%s(.*)\%s(.*)" % (
                            self.config['start_delimiter'],
                            self.config['end_delimiter'],
                            )

                if not re.match(pattern, item):
                    continue

                for key,value in sorted(self._vars.items()):
                    if key in self._word_map:
                        continue

                    pattern = "(.*)\%s(%s)\%s(.*)" % (
                        self.config['start_delimiter'],
                        key,
                        self.config['end_delimiter'],
                        )

                    m = re.match(pattern, item)
                    if m:
                        map_key = "%s%s%s" % (
                            self.config['start_delimiter'],
                            m.group(2),
                            self.config['end_delimiter'],
                            )
                        self._word_map[map_key] = str(value)
                    else:
                        pattern = "(.*)\%s(%s)\.([_a-z0-9]*)\%s(.*)" % (
                            self.config['start_delimiter'],
                            key,
                            self.config['end_delimiter'],
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
                                self.config['start_delimiter'],
                                m.group(2),
                                m.group(3),
                                self.config['end_delimiter'],
                                )
                            self._word_map[new_key] = fixed

        # actually replace the text
        new_txt = str(txt)
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
                    self.config['start_delimiter'],
                    inj,
                    self.config['end_delimiter'],
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
