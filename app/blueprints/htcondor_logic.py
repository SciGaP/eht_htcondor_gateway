from flask import Blueprint, render_template, request, send_from_directory, jsonify

from .htcondor import checkuser, validate_batch_staging, job_submit_batch

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
    
    # get input parameters
    v = {}
    v['userName'] = args['userName']
    v['dataCollection'] = args["dataCollection"]
    v['dataset'] = args["dataset"]
    v['parameterFile'] = args["parameterFile"]
    v['experimentName'] = args['experimentName']
    v['application'] = "ipole-batch"

    validate_results = validate_batch_staging(input=v)

    return jsonify(validate_results)

# submit batch job
@htcondor_blueprint.route("/htcondor/submit/batch")
def submit_batch():
    """
        parameters:
            userName, experimentId
    """

    args = request.args

    if "dryrun" in args:
        # sleep 60 seconds
        import time
        time.sleep(20)
        return {"submit":"yes","submitInformation":""}
    
    #results = job_submit_batch(username = args['userName'], experimentid = args['experimentId'])

    return jsonify(results)

