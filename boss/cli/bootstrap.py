
import os
import shelve
from tempfile import mkdtemp
from cement.utils import fs
from ..cli.controllers.base import BossBaseController
from .source import SourceManager

def setup_db(app):
    app.extend('db', shelve.open(app.config.get('boss', 'db_path')))

    # Note: Can't use the SourceManager here, because it relies on the db 
    # being setup/extended first.
    if 'sources' not in app.db.keys():
        cache_dir = fs.abspath(mkdtemp(dir=app.config.get('boss', 'cache_dir')))

        app.db['sources'] = dict()
        sources = app.db['sources']
        sources['boss'] = dict(
            label='boss',
            path='https://github.com/datafolklabs/boss-templates.git',
            cache=cache_dir,
            is_local=False,
            last_sync_time='never'
            )
        app.db['sources'] = sources

    if 'templates' not in app.db.keys():
        app.db['templates'] = dict()

def extend_source_manager(app):
    app.extend('sources', SourceManager(app))

def cleanup(app):
    if hasattr(app, 'db'):
        app.db.close()

def load(app):
    app.handler.register(BossBaseController)
    app.hook.register('post_setup', setup_db)
    app.hook.register('post_setup', extend_source_manager)
    app.hook.register('pre_close', cleanup)