from app import app, db, oauth, env, login_manager
from app.models import User

from flask import redirect, render_template, session, url_for, json
from urllib.parse import quote_plus, urlencode
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)


@login_manager.user_loader
def load_user(user_id):
    # Get the user from the database with the given id
    return User.query.get(user_id)


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()

    # Check if the user is already in the database
    user = User.query.filter_by(email=token.get("userinfo").get("email")).first()
    
    # If the user is in the database, update their given and family name plus profile picture
    if user:
        user.nickname = token.get("userinfo").get("nickname")
        user.given_name = token.get("userinfo").get("given_name")
        user.family_name = token.get("userinfo").get("family_name")
        user.profile_picture = token.get("userinfo").get("picture")
        db.session.commit()
        login_user(user)
    # If the user is not in the database, create a new user
    else:
        # Create a new user. Here we are inserting a new row in the
        # users table.
        user = User(
            email=token.get("userinfo").get("email"),
            nickname=token.get("userinfo").get("nickname"),
            given_name=token.get("userinfo").get("given_name"),
            family_name=token.get("userinfo").get("family_name"),
            profile_picture=token.get("userinfo").get("picture"),
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)

    return redirect("/")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
def home():
    return render_template("home.html", user=current_user)

@app.route("/about")
@login_required
def about():
    return render_template("home.html", user=current_user)