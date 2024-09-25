from flask import Blueprint, render_template, request
from app import db

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/signup')
def signup():
    return render_template('EHTGatewayRegister.html')

@auth_blueprint.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    userName = request.form.get('userName')
    return userName

@auth_blueprint.route('/login')
def login():
    return render_template('EHTGatewayLogin.html')

# @auth.route('/logout')
# def logout():
#     return 'Logout'
