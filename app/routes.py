from app import app, db, oauth, env, login_manager
from app.models import User
from app.blueprints import user_logic, website_logic, auth_logic, error_handlers
from app.blueprints import htcondor_logic

app.register_blueprint(website_logic.website_blueprint)
app.register_blueprint(auth_logic.auth_blueprint)
app.register_blueprint(user_logic.login_blueprint)
app.register_blueprint(htcondor_logic.htcondor_blueprint)

