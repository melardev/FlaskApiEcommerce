import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, root_path=os.getcwd(), static_url_path='/static')

app.config.from_object(Config)
db = SQLAlchemy(app)  # , model_class=BaseModel)
migrate = Migrate(app, db)
cache = Cache()

# cors with defaults, which means allow all domains, it is fine for the moment
cors = CORS(app)
bcrypt = Bcrypt()
jwt = JWTManager(app)
