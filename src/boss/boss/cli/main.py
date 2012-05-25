
import os
from cement2.core import foundation, backend
from cement2.core import exc as cement_exc
from boss.cli.controllers.base import BossBaseController
from boss.core.utils import abspath
from boss.core import exc as boss_exc

defaults = backend.defaults('boss', 'answers')
defaults['boss']['data_dir'] = '~/.boss/'

class BossApp(foundation.CementApp):
    class Meta:
        label = 'boss'
        base_controller = BossBaseController
        config_defaults = defaults
        config_files = [
            '/etc/boss/boss.conf',
            '~/.boss.conf',
            '~/.boss/config',
            ]
        default_sources = dict(boss='git@github.com:derks/boss-templates.git')
        
    def validate_config(self):
        # fix up paths
        self.config.set('boss', 'data_dir', 
                        abspath(self.config.get('boss', 'data_dir')))

        # create directories
        if not os.path.exists(self.config.get('boss', 'data_dir')):
            os.makedirs(self.config.get('boss', 'data_dir'))
    
        # add shortcuts
        pth = os.path.join(self.config.get('boss', 'data_dir'), 'cache')
        if not os.path.exists(abspath(pth)):
            os.makedirs(abspath(pth))
        self.config.set('boss', 'cache_dir', pth)
    
        pth = os.path.join(self.config.get('boss', 'data_dir'), 'boss.db')
        self.config.set('boss', 'db_path', pth)

def main(*args, **kw):
    app = BossApp(*args, **kw)
    try:
        from boss.cli.bootstrap import base
        app.setup()
        app.run()
    except boss_exc.BossArgumentError as e:
        print "BossArgumentError: %s" % e.msg
    except cement_exc.CementSignalError as e:
        print
        print e
    finally:
        app.close()

if __name__ == '__main__':
    main()