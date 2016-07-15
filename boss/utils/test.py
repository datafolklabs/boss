
from ..cli.main import BossApp, CONFIG_DEFAULTS
from cement.utils.test import *
from cement.utils.misc import rando

class BossTestApp(BossApp):
    class Meta:
        label = "boss-test-%s" % rando()[:12]
        argv = []
        config_files = []

class BossTestCase(CementTestCase):
    app_class = BossTestApp

    def setUp(self):
        super(BossTestCase, self).setUp()
        CONFIG_DEFAULTS['boss']['data_dir'] = self.tmp_dir
        self.app = self.make_app(config_defaults=CONFIG_DEFAULTS)
