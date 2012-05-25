
import os
import sys
import shutil
import shelve
import json
import re
from urllib2 import urlopen, HTTPError
from tempfile import mkdtemp
from datetime import datetime
from cement2.core.controller import CementBaseController, expose
from boss.core.utils import abspath, exec_cmd2
#from boss.core.db import JsonDB
from boss.core import exc as boss_exc
    
class BossAbstractBaseController(CementBaseController):
    def _setup(self, *args, **kw):
        super(BossAbstractBaseController, self)._setup(*args, **kw)
        
class SourceManager(object):
    def __init__(self, app):
        self.app = app
        
    def sync(self, source):
        sources = self.app.db['sources']
        src = self.app.db['sources'][source]
        if not src['is_local']:
            if not os.path.exists(os.path.join(src['cache'], '.git')):
                exec_cmd2([ 'git', 'clone', 
                            src['path'], src['cache'] ])
            else:
                os.chdir(src['cache'])
                exec_cmd2(['git', 'pull'])
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
    
    def get_template_config(self, source, template):
        src = self.app.db['sources'][source]
        if src['is_local']:
            basedir = src['path']
        else:
            basedir = src['cache']
            
        full_path = os.path.join(basedir, template, 'boss.json')
        f = open(full_path)
        config = json.load(f)
        f.close()
        return config
        
    def _fix_file(self, file_name, file_data, variables):
        for var in variables:
            # modify file name
            file_name = re.sub(var, variables[var], file_name)
            
            # modify file content
            file_data = re.sub(var, variables[var], file_data)
            
        return (file_name, file_data)
        
    def create_from_template(self, source, template, dest_dir):
        src = self.app.db['sources'][source]
        config = self.get_template_config(source, template)
        _vars = dict()
        if config.has_key('variables'):
            for question,_var in config['variables']:
                if self.app.config.has_key('answers', _var.lower()):
                    default = self.app.config.get('answers', _var.lower())
                    res = raw_input("%s: [%s] " % (question, default))
                    if len(res) == 0:
                        res = default
                else:
                    res = raw_input("%s: " % question)
                _vars[_var] = res.strip()
        
        if src['is_local']:
            basedir = os.path.join(src['path'], template)
        else:
            basedir = os.path.join(src['cache'], template)
            
        print '-' * 78
        for pth in os.walk(basedir):
            new_basedir = re.sub(basedir, dest_dir, pth[0])
            for _file in pth[2]:
                full_path = abspath(os.path.join(pth[0], _file))
                
                if _file == 'boss.json':
                    continue
                dest_file = abspath(os.path.join(new_basedir, _file))
                
                f = open(full_path, 'r')
                data = f.read()
                f.close()
                
                dest_file, data = self._fix_file(dest_file, data, _vars)
                
                if os.path.exists(dest_file):
                    print 'File Exists: %s' % dest_file
                    continue
                else:
                    print 'Writing: %s' % dest_file
                    
                    if not os.path.exists(os.path.dirname(dest_file)):
                        os.makedirs(os.path.dirname(dest_file))
                        
                    f = open(dest_file, 'w')
                    f.write(data)
                    f.close()
        
        # setup external files
        if config.has_key('external_files'):
            for _file in config['external_files']:
                new_basedir = abspath(re.sub(basedir, dest_dir, basedir))
                dest_file = abspath(os.path.join(new_basedir, _file[0]))
                url, _ = self._fix_file(_file[1], '', _vars)
                try:
                    data = urlopen(url).read()
                except HTTPError as e:
                    data = ''

                dest_file, data = self._fix_file(dest_file, data, _vars)
                
                if os.path.exists(dest_file):
                    print 'File Exists: %s' % dest_file
                    continue
                else:
                    print 'Writing: %s' % dest_file
                    
                    if not os.path.exists(os.path.dirname(dest_file)):
                        os.makedirs(os.path.dirname(dest_file))
                        
                    f = open(dest_file, 'w')
                    f.write(data)
                    f.close()
                    
class BossBaseController(BossAbstractBaseController):
    class Meta:
        label = 'boss'
        description = 'Boss Templates and Development Utilities'
        arguments = [
            (['-t', '--template'], 
             dict(help="a template label", dest='template')),
            (['--local'], 
             dict(help='toggle a local source repository', 
                  action='store_true', default=False)),
            (['modifier1'], dict(help='command modifier', nargs='?')),
            (['modifier2'], dict(help='command modifier', nargs='?')),
            ]
        config_defaults = dict()
    
    @expose(hide=True)
    def default(self):
        print "A sub-command is required.  Please see --help."
        sys.exit(1)
        
    @expose(help="create project files from a template")
    def create(self):
        if not self.app.pargs.modifier1:
            raise boss_exc.BossArgumentError("Destination path required.")
            
        if not self.app.pargs.template:
            raise boss_exc.BossArgumentError("Template label required.")
        
        sources = self.app.db.get('sources', self.app._meta.default_sources)    
        
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
        print
        sources = self.app.db['sources']
        for label in sources:
            print "%s Templates" % label.capitalize()
            print '-' * 78
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
                print tmpl
                
            print

    @expose(help="sync a source repository")
    def sync(self):
        _sources = self.app.db['sources']
        for label in self.app.db['sources']:
            print "Syncing %s Templates . . . " % label.capitalize()
            src = SourceManager(self.app)
            src.sync(label)
            print
            
    @expose(help="list template source repositories")
    def sources(self):
        for key in self.app.db['sources']:
            src = self.app.db['sources'][key]
            print
            print "--        Label: %s" % src['label']
            print "    Source Path: %s" % src['path']
            print "          Cache: %s" % src['cache']
            print "     Local Only: %s" % src['is_local']
            print " Last Sync Time: %s" % src['last_sync_time']
        print
            
    @expose(help="add a template source repository")
    def add_source(self):
        if not self.app.pargs.modifier1 or not self.app.pargs.modifier2:
            raise boss_exc.BossArgumentError("Repository name and path required.")
            
        sources = self.app.db['sources']
        label = self.app.pargs.modifier1
        path = self.app.pargs.modifier2
        cache_dir = mkdtemp(dir=self.app.config.get('boss', 'cache_dir'))

        if self.app.pargs.local:
            path = abspath(path)
            
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
    
            
    