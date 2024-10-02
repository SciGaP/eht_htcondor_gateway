from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/signup')
def signup():
    return render_template('EHTGatewayRegister.html')

@auth_blueprint.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    # user model: email, nickname, given_name, family_name, profile_picture

    nickname = request.form.get('userName')
    given_name = request.form.get('firstName')
    family_name = request.form.get('lastName')
    email = request.form.get('email')
    password = request.form.get('password')
    # temporary host
    profile_picture = "https://eht.scigap.org/media/images/32602803.original.png"

    # Check if the user is already in the database
    user = User.query.filter_by(email=email).first()
    
    # register user 
    if not user:
        user = User(
            email=email,
            nickname=nickname,
            given_name=given_name,
            family_name=family_name,
            password = password,
            profile_picture=profile_picture,
            account_type = "local"
        )
        db.session.add(user)
        db.session.commit()
        return render_template("EHTGatewayThankYouforRegistering.html", useremail = email)
    else:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    
    

@auth_blueprint.route('/login')
def login():
    return render_template('EHTGatewayLogin.html')

@auth_blueprint.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('userName')
    password = request.form.get('password')

    if "@" in username:
        user = User.query.filter_by(email=username).first()
    else:
        user = User.query.filter_by(nickname=username).first()
    
    if not user:
        flash(f'{username} is not found.')
        return redirect(url_for('auth.login'))

    if not (password == user.password):
        flash('Please check your login details.')
        return redirect(url_for('auth.login'))
    
    return "login!"

def login():
    return render_template('EHTGatewayLogin.html')

# @auth.route('/logout')
# def logout():
#     return 'Logout'
