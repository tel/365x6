from __future__ import with_statement
from contextlib import closing
import os.path
import os
import sqlite3

from fabric.api import *
from fabric.utils import puts, warn

import app365.app as app

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
        image = app.Image.fromfile(db, os.path.expanduser(path), photographer.lower().capitalize())
        image.store(db)
        day = app.Day.current(db)
        app.link_image(db, image, day)
        db.commit()
    local('rm %s' % path)

def serve():
    app.app.run(debug=True)

def make_sdist():
    with cd(HOME):
        with settings(warn_only = True):
            local("rm -r dist")
        local("python setup.py sdist")
        return local("ls dist")

@hosts("photo365@photo365.kronka.com")
def deploy(env = "~/pyenv"):
    name = make_sdist()
    put(os.path.join(HOME, "dist", name), "~/tmp/") 
    with cd("~/tmp/"):
        with settings(warn_only = True):
            run("~/run/bin/pip -E %s uninstall app365" % env)
        run("~/run/bin/pip -E %s install %s" % (env, name))
        run("rm %s" % name)
    with cd("~/photo365.kronka.com"):
        run("touch tmp/restart.txt")
