
import os
import shelve
from tempfile import mkdtemp
from cement.core import hook, handler
from cement.utils import fs

def setup_db(app):
    app.extend('db', shelve.open(app.config.get('boss', 'db_path')))
    if 'sources' not in app.db.keys():
        cache_dir = fs.abspath(mkdtemp(dir=app.config.get('boss', 'cache_dir')))

        app.db['sources'] = dict()
        sources = app.db['sources']
        sources['boss'] = dict(
            label='boss',
            path='https://github.com/derks/boss-templates.git',
            cache=cache_dir,
            is_local=False,
            last_sync_time='never'
            ) 
        app.db['sources'] = sources

    if 'templates' not in app.db.keys():
        app.db['templates'] = dict()
        
def cleanup(app):
    if hasattr(app, 'db'):
        app.db.close()

def load():
    hook.register('post_setup', setup_db)
    hook.register('pre_close', cleanup)