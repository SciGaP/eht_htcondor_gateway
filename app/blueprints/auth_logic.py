from flask import Blueprint, render_template
from app import db

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/signup')
def signup():
    return render_template('EHTGatewayRegister.html')

# @auth.route('/login')
# def login():
#     return 'Login'

# @auth.route('/logout')
# def logout():
#     return 'Logout'
