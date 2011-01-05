from __future__ import with_statement
import contextlib
from collections import defaultdict

import sqlite3
import hashlib
import Image as PIL
import os.path

from flask import *
import config

app = Flask(__name__)
app.config.from_object(config)
app.config.from_envvar('365X6_SETTINGS', silent = True)

def get_db():
    return sqlite3.connect(app.config['DATABASE'])

def get_photographer(db, name):
    cur = db.execute('select id from photographers where name = ?;', (name,))
    id = cur.fetchone()[0]
    if id == None:
        raise Exception("Photographer %s does not exist." % name)
    return id

class Image(object):
    __slots__ = ('id', 'photographer', 'description', 'hash', 'path')
    
    @classmethod
    def fromfile(cls, db, path, photographer, description = None):
        im = cls()
        im.description = description
        im.path = path
        im.photographer = get_photographer(db, photographer)
        with open(path) as f:
            im.hash = hashlib.md5(f.read()).hexdigest()
        return im

    @classmethod
    def fromhash(cls, hash):
        im = cls()
        im.hash = hash
        return im

    def store(self, db):
        # Check to see if this file already is stored
        cur = db.execute('select id from photos where hash = (?);', (self.hash,))
        results = cur.fetchall()
        if len(results) == 0:
            # Save the copies
            pil = PIL.open(self.path)
            sz = app.config['THUMB_SIZE']
            thumb = pil.resize((sz, sz), PIL.ANTIALIAS)
            sz = app.config['FULL_SIZE']
            if pil.size[0] < sz:
                sz = pil.size[0]
            full = pil.resize((sz, sz), PIL.ANTIALIAS)
            pil.save(self.basepath())
            full.save(self.fullpath())
            thumb.save(self.thumbpath())
            # Update the database
            cur = db.execute("""
                insert into photos (description, photographer, hash) values (?, ?, ?)
                """, (self.description, self.photographer, self.hash))
            self.id = cur.lastrowid
        else:
            # Image already stored, update the row id
            self.id = results[0][0]
        return self

    def basepath(self):
        return os.path.join(app.config['IMAGE_PATH'], self.hash + '.jpg')

    def fullpath(self):
        return os.path.join(app.config['IMAGE_PATH'], self.hash + '_full.jpg')

    def thumbpath(self):
        return os.path.join(app.config['IMAGE_PATH'], self.hash + '_thumb.jpg')

    def fullurl(self):
        return app.config['IMAGE_URL'] + self.hash + '_full.jpg'

    def thumburl(self):
        return app.config['IMAGE_URL'] + self.hash + '_thumb.jpg'

class Day(object):
    __slots__ = ('id', 'color', 'date')

    def __init__(self, vals):
        self.id, self.color, self.date = vals

    @classmethod
    def today(cls, db):
        cur = db.execute("select id, ts, color from days where date(ts) = date('now');")
        res = cur.fetchone() 
        if res == None:
            # Create today
            cur.execute("insert into days default values;")
            day = cls.by_id(db, cur.lastrowid)
        else:
            # Restore today
            day = cls(res)
        return day

    @classmethod
    def current(cls, db):
        cur = db.execute("""
                select days.*
                from days, state 
                where days.id = state.content 
                    and state.name like 'current_day';
            """)
        res = cur.fetchall()
        if len(res) != 1:
            raise Exception("State table of database is incomplete: no current day set.")
        return cls(res[0])

    @classmethod
    def by_id(cls, db, id):
        cur = db.execute("select id, ts, color from days where id = ?;", str(id))
        return cls(cur.fetchone())

def link_image(db, image, day):
    try:
        db.execute("insert into joiner (photo_id, day_id, photographer_id) values (?, ?, ?);",
                    (image.id, day.id, image.photographer))
    except sqlite3.IntegrityError:
        db.execute("update joiner set photo_id = ? where day_id = ? and photographer_id = ?;", 
                    (image.id, day.id, image.photographer))

@app.before_request
def before_request():
    g.db = get_db()
    g.static = lambda path: app.config['STATIC_URL'] + path

@app.after_request
def after_request(response):
    g.db.close()
    return response

def get_images(day):
    query = """
    select photographers.name, photos.hash 
    from joiner, photographers, photos, days 
    where days.id = ?
        and days.id = joiner.day_id 
        and photos.id = joiner.photo_id 
        and photos.photographer = photographers.id
    order by photographers.id asc;
    """
    cur = g.db.execute(query, [day.id])
    rows = cur.fetchall()

    names = ['Joe', 'Henry', 'Janet', 'Megan', 'Kento', 'Chanh']
    images = defaultdict(lambda: Image.fromhash('missing'))
    for name, hash in rows:
        images[name] = Image.fromhash(hash)
    return names, images

@app.route('/')
def index():
    day = Day.current(g.db)
    names, images = get_images(day)

    return render_template('index.html', current = day, day = day, images=images, names=names)

@app.route('/day/<id>/')
def view_day(id):
    id = int(id)
    current = Day.current(g.db)
    if id > current.id:
        abort(404)
    day = Day.by_id(g.db, id)
    names, images = get_images(day)
    
    return render_template('index.html', current = current, day =day, images = images, names = names)

@app.errorhandler(404)
def not_found(e):
    return "Not found."

if __name__ == '__main__':
    from flaskext.lesscss import lesscss
    lesscss(app)
    app.run(debug=True)
