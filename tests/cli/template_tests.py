
import os
import shutil
from boss.core import exc
from boss.cli.main import main
from boss.utils import test

@test.attr('template')
class TemplateTestCase(test.BossTestCase):
    def test_json_config_file(self):
        # setup the default app first to add the sources
        with self.app as app:
            # create a fake template
            data_dir = self.app.config.get('boss', 'data_dir')
            os.makedirs(os.path.join(data_dir, self.rando))
            f = open(os.path.join(data_dir, self.rando, 'boss.json'), 'w')
            f.write('{"fake": "json}')
            f.close()
            app.sources.add(self.rando, self.tmp_dir, local=True) 
            app.sources.sync(self.rando)
