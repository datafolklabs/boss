
import os
from cement2.core import foundation, backend
from boss.cli.controllers.base import BossBaseController
from boss.core.utils import abspath

defaults = backend.defaults('boss')
defaults['boss']['data_dir'] = '~/.boss/'
defaults['boss']['auto_update'] = True

class BossApp(foundation.CementApp):
    class Meta:
        label = 'boss'
        base_controller = BossBaseController
        config_defaults = defaults
        default_sources = dict(boss='git@github.com:derks/boss-templates.git')
        
    def validate_config(self):
        # fix up paths
        self.config.set('boss', 'data_dir', 
                        abspath(self.config.get('boss', 'data_dir')))
        
        # fix up sources list
        res = self.config.get('boss', 'sources')
        final_sources = []
        if type(res) == str:
            sources = res.split(' ')
            for source in sources:
                final = source.strip('\\ \n')
                if len(final) > 0:
                    final_sources.append(final)
            self.config.set('boss', 'sources', final_sources)
            
        # create data directory
        if not os.path.exists(self.config.get('boss', 'data_dir')):
            os.makedirs(self.config.get('boss', 'data_dir'))

        # add shortcuts
        pth = os.path.join(self.config.get('boss', 'data_dir'), 'templates')
        self.config.set('boss', 'template_dir', pth)
    
        pth = os.path.join(self.config.get('boss', 'data_dir'), 'boss.db')
        self.config.set('boss', 'db_path', pth)

def main(*args, **kw):
    app = BossApp(*args, **kw)
    try:
        app.setup()
        from boss.cli.bootstrap import base
        app.run()
    finally:
        app.close()

if __name__ == '__main__':
    main()