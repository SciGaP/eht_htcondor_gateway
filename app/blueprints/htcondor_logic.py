from flask import Blueprint, render_template, request, send_from_directory, jsonify

from .htcondor import checkuser

htcondor_blueprint = Blueprint("htcondor", __name__)

@htcondor_blueprint.route("/htcondor/")
def htccondor_root():
    return "htcodor api root"

@htcondor_blueprint.route("/htcondor/<username>")
def userinfo(username):
    response = checkuser(username)
    
    return jsonify(response)