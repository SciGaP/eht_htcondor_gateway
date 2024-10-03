from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from os import environ as env
import os

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

oauth.register(
    "cilogon",
    client_id=env.get("CILOGON_CLIENT_ID"),
    client_secret=env.get("CILOGON_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("CILOGON_DOMAIN")}/.well-known/openid-configuration'
)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Initialize the database
app.config['SQLALCHEMY_DATABASE_URI'] = env.get("DATABASE_URL")
db = SQLAlchemy(app)

# Setup migration rules
migrate = Migrate(app, db)
migrate = Migrate(app, db, command='db')

# Setup Whoosh index for search
index_dir = 'index'
if not os.path.exists(index_dir):
    os.mkdir(index_dir)
    
schema = Schema(content=TEXT(stored=True))
ix = create_in(index_dir, schema=schema)

from app import routes