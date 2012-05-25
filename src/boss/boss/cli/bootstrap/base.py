
import os
import shelve
from tempfile import mkdtemp
from cement2.core import hook
from boss.core.utils import abspath

@hook.register(name='cement_post_setup_hook')
def post_setup(app):
    app.extend('db', shelve.open(app.config.get('boss', 'db_path')))
    if not app.db.has_key('sources'):
        cache_dir = abspath(mkdtemp(dir=app.config.get('boss', 'cache_dir')))
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        source = dict(
            label='boss',
            path='git@github.com:derks/boss-templates.git',
            cache=cache_dir,
            is_local=False,
            last_sync_time='never'
            ) 
        app.db['sources'] = dict()
        app.db['sources']['boss'] = source

    if not app.db.has_key('templates'):
        app.db['templates'] = dict()
        
@hook.register(name='cement_on_close_hook')
def on_close(app):
    if hasattr(app, 'db'):
        app.db.close()