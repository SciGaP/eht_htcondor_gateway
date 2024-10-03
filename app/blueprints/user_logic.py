from app import app, db, oauth, env, login_manager
from app.models import User

from flask import redirect, render_template, session, url_for, json, Blueprint
from urllib.parse import quote_plus, urlencode
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

login_blueprint = Blueprint("user", __name__)

@login_manager.user_loader
def load_user(user_id):
    # Get the user from the database with the given id
    user = User.query.get(user_id)
    
    app.logger.debug(f"{user} loaded from database")
    return user

@login_manager.unauthorized_handler
def login():
    app.logger.info("An unauthorized user tried to access a protected page")
    return redirect(url_for("user.login"))

@login_blueprint.route("/cilogin")
def cilogin():
    app.logger.debug("Redirecting to the Auth0 login page")
    print(url_for("user.callback"))
    return oauth.cilogon.authorize_redirect(
        redirect_uri=url_for("user.callback", _external=True)
    )


@login_blueprint.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.cilogon.authorize_access_token()
    app.logger.debug(f"Successful callback from Auth0 with token: {token}")

    # Check if the user is already in the database
    user = User.query.filter_by(email=token.get("userinfo").get("email"),account_type="cilogon").first()
    
    # If the user is in the database, update their given and family name plus profile picture
    if user:
        # user.nickname = token.get("userinfo").get("nickname")
        # user.given_name = token.get("userinfo").get("given_name")
        # user.family_name = token.get("userinfo").get("family_name")
        # user.profile_picture = token.get("userinfo").get("picture")
        # db.session.commit()
        login_user(user)

        app.logger.info(f"{user} retrieved from database and logged in")
    # If the user is not in the database, create a new user
    else:
        # Create a new user. Here we are inserting a new row in the
        # users table.
        import uuid
        user = User(
            id=str(uuid.uuid4()),
            email=token.get("userinfo").get("email"),
            nickname=token.get("userinfo").get("name"),
            given_name=token.get("userinfo").get("given_name"),
            family_name=token.get("userinfo").get("family_name"),
            password = "",
            profile_picture="https://eht.scigap.org/media/images/32602803.original.png",
            account_type = "cilogon",
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)

        app.logger.info(f"{user} created in the database and logged in")

    return redirect("/dashboard")


@login_blueprint.route("/logout")
def logout():
    app.logger.info(f"{current_user} logged out")
    logout_user()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("website.home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )
