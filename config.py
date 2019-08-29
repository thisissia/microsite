import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hiiiiii'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:''@localhost/app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
