from __future__ import with_statement
from contextlib import closing
import os.path

from fabric.api import *
from fabric.utils import puts, warn

import app

HOME = os.path.dirname(__file__)

def backup_db(filename = 'backup.sql'):
    with cd(HOME):
        local('echo ".dump" | sqlite3 db > %s' % filename)
    
def rebuild_db():
    backup_db('database.old.sql')
    puts("Old database backed up to database.old.sql")
    with cd(HOME):
        local('sqlite3 db < schema.sql')

def update_day():
    with closing(app.get_db()) as db:
        # Refresh today
        day = app.Day.today(db)
        db.commit()

def add_image(photographer, path):
    with closing(app.get_db()) as db:
        image = app.Image.fromfile(db, path, photographer.lower().capitalize())
        image.store(db)
        day = app.Day.current(db)
        app.link_image(db, image, day)
        db.commit()
    local('rm %s' % path)
