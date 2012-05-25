
import os
import sys
import shutil
import shelve
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
    def __init__(self, db):
        self.db = db
        
    def sync(self, source):
        sources = self.db['sources']
        src = self.db['sources'][source]
        if not src['is_local']:
            if not os.path.exists(src['cache']):
                exec_cmd2([ 'git', 'clone', 
                            src['path'], src['cache'] ])
            else:
                os.chdir(src['cache'])
                exec_cmd2(['git', 'pull'])
        src['last_sync_time'] = datetime.now()
        sources[source] = src
        self.db['sources'] = sources
    
    def get_templates(self, source):
        templates = []
        src = self.db['sources'][source]
        for entry in os.listdir(src['cache']):
            full_path = os.path.join(src['cache'], entry)
            if entry.startswith('.'):
                continue
            elif os.path.isdir(full_path):
                templates.append(entry)
        return templates
    
    def get_template_config(self, source, template):
        src = self.db['sources'][source]
        full_path = os.path.join(src['local_path'], template)
        sys.path.insert(0, full_path)
        my_mod = __import__('boss_config', globals(), locals(), [], -1)
        sys.path.pop(0)
        return my_mod
        
    def create_from_template(self, source, template, dest_path):
        src = self.db['sources'][source]
        mod = self.get_template_config(source, template)
        _vars = dict()
        for question,_var in mod.VARIABLES:
            res = raw_input("%s: " % question)
            _vars[_var] = res.strip()
        print _vars
        
class BossBaseController(BossAbstractBaseController):
    class Meta:
        label = 'boss'
        description = 'Boss Templates and Development Utilities'
        arguments = [
            (['-t', '--template'], 
             dict(help="a template label", dest='template')),
            (['--local'], 
             dict(help='local source repository', 
                  action='store_true', default=False)),
            (['--remote'], dict(help='remote source repository')),
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
            raise boss_exc.BossArgumentError("Project name required.")
            
        if not self.app.pargs.template:
            raise boss_exc.BossArgumentError("Template label required.")
        
        sources = self.app.db.get('sources', self.app._meta.default_sources)    
        
        try:
            tmpl_parts = self.app.pargs.template.split(':')
            source_label = tmpl_parts[0]
            template = tmpl_parts[1]
        except IndexError as e:
            source_label = 'boss'
            template = self.app.pargs.template
        
        if source_label == 'local':
            src = Source(source_label, None, sources[source_label])
        else:
            local_path = "%s/templates/%s" % (
                    self.app.config.get('boss', 'data_dir'), source_label,
                    )
            src = Source(source_label, sources[source_label], local_path)
         
        src.create_from_template(template, 
                                 self.app.config.get('boss', 'project_dir'))

    @expose(help="list all available templates", aliases=['list-templates'])
    def list(self):
        print
        sources = self.app.db['sources']
        for label in sources:
            print "%s Templates (%s)" % (label.capitalize(), sources[label])
            print '-' * 78
            if label == 'local':
                local_path = sources[label]
                remote_path = None
            else:
                local_path = "%s/templates/%s" % (
                            self.app.config.get('boss', 'data_dir'), label,
                            )
                remote_path = sources[label]
                        
            src = SourceManager(self.app.db)
            for tmpl in src.get_templates(label):
                print tmpl
                
            print

    @expose(help="sync a source repository")
    def sync(self):
        _sources = self.app.db['sources']
        for label in self.app.db['sources']:
            print "Syncing %s Templates . . . " % label.capitalize()
            src = SourceManager(self.app.db)
            src.sync(label)
            print
            
    @expose(help="list template source repositories")
    def list_sources(self):
        for key in self.app.db['sources']:
            src = self.app.db['sources'][key]
            print
            print "--        Label: %s" % key
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
    
            
    