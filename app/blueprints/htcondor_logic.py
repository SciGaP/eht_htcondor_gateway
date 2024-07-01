from flask import Blueprint, render_template, request, send_from_directory, jsonify

from .htcondor import checkuser, get_experimentid

htcondor_blueprint = Blueprint("htcondor", __name__)

@htcondor_blueprint.route("/htcondor/")
def htccondor_root():
    return "htcodor api root"

@htcondor_blueprint.route("/htcondor/<username>")
def userinfo(username):
    response = checkuser(username)
    
    return jsonify(response)

# validate the batch job
@htcondor_blueprint.route("/htcondor/validate/batch")
def validate_batch():
    """
        validate batch job
        parameters:
            userName
            experimentName
            dataCollection
            dataset
            parameterFile
        return:
            experimentId
            expectedOutput
            outputSize
    """
    args = request.args
    v = {}
    v['userName'] = args['userName']
    v['dataCollection'] = args["dataCollection"]
    v['dataset'] = args["dataset"]
    v['parameterFile'] = args["parameterFile"]
    v['experimentName'] = args['experimentName']
    v['eperimentId'] = get_experimentid(username = v['userName'])
    v['expectedOutput'] = 32600
    v['outputSize'] = "260 GB"

    return jsonify(v)

