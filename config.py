import os
basedir = os.path.abspath((os.path.dirname(__file__)))

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
ARTICLES_PER_PAGE = 10
SECRET_KEY = 'secret key to protect from csrf'