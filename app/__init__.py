from os import environ as env

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

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

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Initialize the database
app.config['SQLALCHEMY_DATABASE_URI'] = env.get("DATABASE_URL")
db = SQLAlchemy(app)

# Setup migration rules
migrate = Migrate(app, db)
migrate = Migrate(app, db, command='db')

from app import routes