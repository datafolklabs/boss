
import os
import sys
from tempfile import mkdtemp
from cement.core import foundation
from cement.core import exc as cement_exc
from cement.utils import fs, misc
from boss.cli.controllers.base import BossBaseController
from boss.core import exc as boss_exc

if sys.version_info[0] >= 3:
    from imp import reload      # pragma: nocover

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

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    app = BossApp(argv=argv)
    try:
        app.setup()
        app.run()
    except boss_exc.BossTemplateError as e:
        print("BossTemplateError: %s" % e.msg)
    except boss_exc.BossArgumentError as e:
        print("BossArgumentError: %s" % e.msg)
    except cement_exc.CaughtSignal as e:        # pragma: nocover
        print(e)                                # pragma: nocover
    except cement_exc.FrameworkError as e:      # pragma: nocover
        print(e)                                # pragma: nocover

    app.close()

test_tmpdir = mkdtemp()
def get_test_app(**kw):
    test_defaults = defaults
    test_defaults['boss']['data_dir'] = test_tmpdir
    kw['config_defaults'] = kw.get('config_defaults', test_defaults)
    kw['config_files'] = kw.get('config_files', [])

    app = BossApp(**kw)
    return app

if __name__ == '__main__':
    main()  # pragma: nocover
