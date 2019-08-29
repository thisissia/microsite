import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hiiiiii'
    SQLALCHEMY_DATABASE_URI = 'mysql://mysql:720a706c4f6c9bac@dokku-mysql-microsite:3306/microsite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
