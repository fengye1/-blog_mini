#coding:utf-8
from flask_sqlalchemy import  SQLAlchemy
from flask import Flask
from  flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_openid import OpenID
from config import basedir
from flask_wtf.csrf import CSRFProtect
import os



app = Flask(__name__)
app.config.from_object('config')

db=SQLAlchemy(app)

bootstrap = Bootstrap(app)

moment = Moment(app)

login_manager = LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'
login_manager.init_app(app)

CSRFProtect(app)

oid = OpenID(app, os.path.join(basedir, 'tmp'))

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint,url_prefix='/auth')

from .admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint,url_prefix='/admin')

from app import modles
