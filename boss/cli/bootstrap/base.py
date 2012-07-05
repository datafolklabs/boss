
import os
import shelve
from tempfile import mkdtemp
from cement.core import hook, handler
from cement.utils import fs

@hook.register(name='cement_post_setup_hook')
def post_setup(app):
    app.extend('db', shelve.open(app.config.get('boss', 'db_path')))
    if 'sources' not in app.db.keys():
        cache_dir = fs.abspath(mkdtemp(dir=app.config.get('boss', 'cache_dir')))

        app.db['sources'] = dict()
        sources = app.db['sources']
        sources['boss'] = dict(
            label='boss',
            path='git@github.com:derks/boss-templates.git',
            cache=cache_dir,
            is_local=False,
            last_sync_time='never'
            ) 
        app.db['sources'] = sources

    if 'templates' not in app.db.keys():
        app.db['templates'] = dict()
        
@hook.register(name='cement_on_close_hook')
def on_close(app):
    if hasattr(app, 'db'):
        app.db.close()