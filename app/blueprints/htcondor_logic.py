import json
from flask import Blueprint, render_template, request, send_from_directory, jsonify

from .htcondor import (
    checkuser,
    validate_batch_staging,
    job_submit_batch,
    validate_explorer_staging,
    job_submit_explorer,
    release_job,
    kill_job,
    finish_job,
)

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
    v["userName"] = args["userName"]
    v["dataCollection"] = args["dataCollection"]
    v["dataset"] = args["dataset"]
    v["parameterFile"] = args["parameterFile"]
    v["experimentName"] = args["experimentName"]
    v["application"] = "ipole-batch"

    validate_results = validate_batch_staging(input=v)

    return jsonify(validate_results)


# validate the explorer job
@htcondor_blueprint.route("/htcondor/validate/explorer")
def validate_explorer():
    """
    validate batch job
    parameters:
        userName
        experimentName
        dataCollection
        dataset
        imageList
        parameters
    return:
        experimentId
        expectedOutput
        outputSize
    """
    args = request.args

    # get input parameters
    v = {}
    v["userName"] = args["userName"]
    v["dataCollection"] = args["dataCollection"]
    v["dataset"] = args["dataset"]
    # use default data set
    v["dataset"] = "Ma+0.94_w4"
    v["experimentName"] = args["experimentName"]
    v["application"] = "ipole-explorer"
    v["imageList"] = args["imageList"]
    # convert to to dict object from a string
    v["parameters"] = json.loads(args["parameters"])

    validate_results = validate_explorer_staging(input=v)

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
        # sleep 20 seconds
        import time

        time.sleep(20)
        return {"submit": "yes", "submitInformation": ""}

    results = job_submit_batch(
        username=args["userName"], experimentid=args["experimentId"]
    )

    return jsonify(results)


# submit explorer job
@htcondor_blueprint.route("/htcondor/submit/explorer")
def submit_explorer():
    """
    parameters:
        userName, experimentId
    """

    args = request.args

    if "dryrun" in args:
        # sleep 10 seconds
        import time

        time.sleep(10)
        return {"submit": "yes", "submitInformation": ""}

    results = job_submit_explorer(
        username=args["userName"], experimentid=args["experimentId"]
    )

    return jsonify(results)


# release the job
@htcondor_blueprint.route("/htcondor/release/<experimentid>")
def job_release(experimentid):
    """release the job"""
    results = release_job(experimentid=experimentid)
    return jsonify(results)


# stop the job
@htcondor_blueprint.route("/htcondor/stop/<experimentid>")
def job_stop(experimentid):
    """stop the job
    -- remove the job from the queue
    -- keep the output
    -- update job json
    """

    return


# kill the job
@htcondor_blueprint.route("/htcondor/kill/<experimentid>")
def job_kill(experimentid):
    """stop the job
    -- remove the job from the queue
    -- delete the output
    -- update job json ("cancelled")
    """
    results = kill_job(experimentid=experimentid)
    return jsonify(results)


# finish the job
@htcondor_blueprint.route("/htcondor/finish/<experimentid>")
def job_finish(experimentid):
    """stop the job
    -- remove the job from the queue
    -- keep the output
    -- update job json ("done")
    """
    results = finish_job(experimentid=experimentid)
    return jsonify(results)
