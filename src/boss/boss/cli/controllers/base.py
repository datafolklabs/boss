
import os
import sys
import shutil
from cement2.core.controller import CementBaseController, expose
from boss.core.utils import abspath, exec_cmd2
from boss.core.db import JsonDB
from boss.core import exc as boss_exc
    
class BossAbstractBaseController(CementBaseController):
    def _setup(self, *args, **kw):
        super(BossAbstractBaseController, self)._setup(*args, **kw)
        self.db = JsonDB(self.app.config.get('boss', 'db_path'))
        self.db.connect()
        
class Source(object):
    def __init__(self, label, remote_path, local_path):
        self.label = label
        self.local_path = local_path
        self.remote_path = remote_path
        
        # hard hack
        if self.label == 'local':
            self.remote_path = None
        
    def sync(self):
        if self.remote_path:
            if not os.path.exists(self.local_path):
                exec_cmd2(['git', 'clone', self.remote_path, self.local_path])
            else:
                os.chdir(self.local_path)
                exec_cmd2(['git', 'pull'])
    
    def get_templates(self):
        templates = []
        for entry in os.listdir(self.local_path):
            full_path = os.path.join(self.local_path, entry)
            if entry.startswith('.'):
                continue
            elif os.path.isdir(full_path):
                templates.append(entry)
        return templates
    
    def get_template_config(self, template):
        full_path = os.path.join(self.local_path, template)
        sys.path.insert(0, full_path)
        my_mod = __import__('boss_config', globals(), locals(), [], -1)
        sys.path.pop(0)
        return my_mod
        
    def create_from_template(self, template, dest_path):
        mod = self.get_template_config(template)
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
        
        sources = self.db.get('sources', self.app._meta.default_sources)    
        
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
        sources = self.db.get('sources', self.app._meta.default_sources)
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
                        
            src = Source(label, remote_path, local_path)
            for tmpl in src.get_templates():
                print tmpl
                
            print

    @expose(help="sync a source repository")
    def sync(self):
        sources = self.db.get('sources', self.app._meta.default_sources)
            
        for label in sources:
            print "Syncing %s Templates . . . " % label.capitalize()
            local_path = "%s/templates/%s" % (
                    self.app.config.get('boss', 'data_dir'), label,
                    )
            src = Source(label, sources[label], local_path)
            src.sync()
            print
            
    @expose(help="list template source repositories")
    def list_sources(self):
        sources = self.db.get('sources', self.app._meta.default_sources)
        for key in sources:
            print "%s: %s" % (key, sources[key])
                                 
    @expose(help="add a template source repository")
    def add_source(self):
        if not self.app.pargs.modifier1 or not self.app.pargs.modifier2:
            raise boss_exc.BossArgumentError("Repository name and path required.")
            
        sources = self.db.get('sources', self.app._meta.default_sources)
        if self.app.pargs.modifier1 == 'local':
            path = abspath(self.app.pargs.modifier2)
        else:
            path = self.app.pargs.modifier2
            
        sources[self.app.pargs.modifier1] = path
        self.db.set('sources', sources)

    @expose(help="remove a source repository")
    def rm_source(self):
        sources = self.db.get('sources', self.app._meta.default_sources)
        
        if not self.app.pargs.modifier1:
            raise boss_exc.BossArgumentError("Repository name required.")
        elif self.app.pargs.modifier1 not in sources:
            raise boss_exc.BossArgumentError("Unknown source repository.")

        
        del sources[self.app.pargs.modifier1]
        
        # don't delete a local template dir, only remotes
        if self.app.pargs.modifier1 != 'local':
            pth = "%s/templates/%s" % (
                self.app.config.get('boss', 'data_dir'),
                self.app.pargs.modifier1,
                )
            if os.path.exists(pth):
                shutil.rmtree(pth)
                
        self.db.set('sources', sources)
    
            
    