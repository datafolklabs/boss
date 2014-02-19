
import os
import sys
from cement.core import foundation
from cement.core import exc as cement_exc
from cement.utils import fs, misc
from boss.cli.controllers.base import BossBaseController
from boss.core import exc as boss_exc

if sys.version_info[0] >= 3:
    from imp import reload

defaults = misc.init_defaults('boss', 'answers')
defaults['boss']['data_dir'] = '~/.boss/'

class BossApp(foundation.CementApp):
    class Meta:
        label = 'boss'
        bootstrap = 'boss.cli.bootstrap'
        base_controller = BossBaseController
        config_defaults = defaults
        config_files = [
            '/etc/boss/boss.conf',
            '~/.boss.conf',
            '~/.boss/config',
            ]

    def validate_config(self):
        # fix up paths
        self.config.set('boss', 'data_dir',
                        fs.abspath(self.config.get('boss', 'data_dir')))

        # create directories
        if not os.path.exists(self.config.get('boss', 'data_dir')):
            os.makedirs(self.config.get('boss', 'data_dir'))

        # add shortcuts
        pth = os.path.join(self.config.get('boss', 'data_dir'), 'cache')
        if not os.path.exists(fs.abspath(pth)):
            os.makedirs(fs.abspath(pth))
        self.config.set('boss', 'cache_dir', pth)

        pth = os.path.join(self.config.get('boss', 'data_dir'), 'boss.db')
        self.config.set('boss', 'db_path', pth)

def main():
    app = BossApp()
    try:
        app.setup()
        app.run()
    except boss_exc.BossTemplateError as e:
        print("BossTemplateError: %s" % e.msg)
    except boss_exc.BossArgumentError as e:
        print("BossArgumentError: %s" % e.msg)
    except cement_exc.CaughtSignal as e:
        print(e)
    except cement_exc.FrameworkError as e:
        print(e)
    finally:
        app.close()

def get_test_app(**kw):
    from tempfile import mkdtemp

    test_defaults = defaults
    test_defaults['boss']['data_dir'] = mkdtemp()
    kw['defaults'] = kw.get('defaults', test_defaults)
    kw['config_files'] = kw.get('config_files', [])
    kw['default_sources'] = kw.get('default_sources', None)

    app = BossApp(**kw)
    return app

if __name__ == '__main__':
    main()
