
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
        
class BossBaseController(BossAbstractBaseController):
    class Meta:
        label = 'boss'
        description = 'Boss Templates and Development Utilities'
        arguments = [
            (['modifier1'], dict(help='command modifier', nargs='?')),
            (['modifier2'], dict(help='command modifier', nargs='?')),
            ]
        config_defaults = dict()
    
    @expose(hide=True)
    def default(self):
        pass
    
    @expose(help="create project files from a template")
    def create(self):
        pass

    @expose(help="list all available templates", aliases=['list-templates'])
    def list(self):
        sources = self.db.get('sources', self.app._meta.default_sources)
        for source in sources:
            path = "%s/templates/%s" % (
                        self.app.config.get('boss', 'data_dir'), source,
                        )
                        
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if entry.startswith('.'):
                    continue
                elif os.path.isdir(full_path):
                    print full_path
                    sys.path.insert(0, full_path)
                    my_mod = __import__('boss_config', globals(), locals(), [], -1)
                    print my_mod
    
    @expose(help="display information for a given template")
    def show(self):
        pass
    
    @expose(help="sync a source repository")
    def sync(self):
        sources = self.db.get('sources', self.app._meta.default_sources)
        sync_sources = []
        if not self.app.pargs.modifier1:
            sync_sources = sources
        else:
            sync_sources = [self.app.pargs.modifier1]
            
        if self.app.pargs.modifier1 and \
           self.app.pargs.modifier1 not in sources:
            raise boss_exc.BossArgumentError("Unknown source repository.")
            
        for source in sync_sources:
            print "Syncing with '%s' upstream . . ." % source
            pth = "%s/templates/%s" % (
                    self.app.config.get('boss', 'data_dir'), source,
                    )
            if not os.path.exists(pth):
                exec_cmd2(['git', 'clone', sources[source], pth])
            else:
                os.chdir(pth)
                exec_cmd2(['git', 'pull'])
            print
            
    @expose(help="list template source repositories")
    def list_sources(self):
        sources = self.db.get('sources', self.app._meta.default_sources)
        for key in sources:
            print "%s: %s" % (key, sources[key])
                                 
    @expose(help="add a template source repository")
    def add_source(self):
        if not self.app.pargs.modifier1 or not self.app.pargs.modifier2:
            raise boss_exc.BossArgumentError("Repository name and url required.")
            
        sources = self.db.get('sources', self.app._meta.default_sources)
        sources[self.app.pargs.modifier1] = self.app.pargs.modifier2
        self.db.set('sources', sources)

    @expose(help="remove a source repository")
    def rm_source(self):
        if not self.app.pargs.modifier1:
            raise boss_exc.BossArgumentError("Repository name required.")
            
        sources = self.db.get('sources', self.app._meta.default_sources)
        if self.app.pargs.modifier1 in sources:
            del sources[self.app.pargs.modifier1]
            pth = "%s/templates/%s" % (
                self.app.config.get('boss', 'data_dir'),
                self.app.pargs.modifier1,
                )
            if os.path.exists(pth):
                shutil.rmtree(pth)
        self.db.set('sources', sources)
    
            
    