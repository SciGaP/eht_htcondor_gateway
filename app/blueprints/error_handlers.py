from app import app

from flask import render_template
from flask_login import current_user

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html', user=current_user, error=e), 404

@app.errorhandler(401)
def unauthorized_access(e):
    return render_template('error_pages/401.html', user=current_user, error=e), 401

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error_pages/500.html', user=current_user, error=e), 500