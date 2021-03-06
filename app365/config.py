import os.path

HOME = os.path.dirname(__file__)
def path(string):
    return os.path.join(HOME, string)

DATABASE = path('db')
DEBUG = True
SECRET_KEY = '456b0a55c74b26316752559e9bc1c39139ef1f1e'
STATIC_PATH = path('static')
STATIC_URL = 'http://localhost:5000/static/'
IMAGE_PATH = STATIC_PATH + '/store'
IMAGE_URL = STATIC_URL + 'store/'
THUMB_SIZE = 270
FULL_SIZE = 800
