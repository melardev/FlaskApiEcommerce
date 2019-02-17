import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    IMAGES_LOCATION = os.path.join(basedir, 'static', 'images')
    # Flask Jwt extended
    # for more info either look at the official page or jwt_manager.py file
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET', 'JWT_SUPER_SECRET')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(10 ** 6)
    JWT_AUTH_USERNAME_KEY = 'username'
    JWT_AUTH_HEADER_PREFIX = 'Bearer'

    # CORS
    CORS_ORIGIN_WHITELIST = [
        'http://localhost:4000'
    ]
