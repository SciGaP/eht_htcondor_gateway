import os, sys, json, re
from datetime import datetime
from dotenv import load_dotenv
from .htcondor_utilities import htcondor_status, run_jobscript, get_outputlist, put_file
from .utilites import parse_values_bytype, append_to_json

load_dotenv()


def get_workspace():
    """get the structure of workspace
    workspace: eht_workspace
    -- users
        -- username
            -- experiment_[id]
    -- staging (holds the files for validation)
    return a dict object
    """
    d_w = {}
    workspace = os.path.expanduser(os.getenv("workspace"))
    d_w["workspace"] = workspace
    d_w["staging"] = os.path.join(workspace, "staging")
    d_w["users"] = os.path.join(workspace, "users")
    if not os.path.exists(d_w["staging"]):
        os.makedirs(d_w["staging"], exist_ok=True)
    if not os.path.exists(d_w["users"]):
        os.makedirs(d_w["users"], exist_ok=True)
    usernames = os.listdir(d_w["users"])
    d_w["usernames"] = usernames
    return d_w


def get_userfolder(username):
    """return the folder for a user"""
    workspace = get_workspace()
    userfolder = os.path.join(workspace["users"], username)
    if not os.path.exists(userfolder):
        os.makedirs(userfolder, exist_ok=True)
    return userfolder


def userhistory(username):
    """check job history of a user"""

    userfolder = get_userfolder(username)
    # find any folder list as experiment
    # experiment_id
    experiments = [
        name
        for name in os.listdir(userfolder)
        if os.path.isdir(os.path.join(userfolder, name))
    ]
    ex_num = len(experiments)
    # need to add jobid back
    experiments = [f"{username}_{x}" for x in experiments]
    return {"experiments": ex_num, "jobids": experiments}


def checkuser(username, simple=False):
    """check user information
    if simple = true, only return
    """
    userstatus = {}
    userstatus["username"] = username
    history = userhistory(username)
    userstatus["experiments"] = history["experiments"]
    userstatus["running"] = 0
    if simple:
        return userstatus

    # check if there is jobs in htcondor
    joblist = htcondor_status()
    if (joblist is None) or (len(joblist) == 0):
        userstatus["running"] = 0
        userstatus["runningExperiments"] = ""
    else:
        jobincondor = [x for x in joblist if username in x["ID"]]
        if len(jobincondor) > 0:
            userstatus["running"] = len(jobincondor)
            userstatus["runningExperiments"] = jobincondor
    # other wise return the full records
    userstatus["inqueue"] = ""
    userstatus["recents"] = userstatus["experiments"] - userstatus["running"]
    userstatus["recents_jobids"] = [
        x for x in history["jobids"] if x not in userstatus["runningExperiments"]
    ]

    return userstatus


def get_experimentid(username):
    """return an experiment id for a user
    experiment id:
    """

    import uuid

    longid = uuid.uuid4()
    uniqueid = username + "-" + str(longid).split("-")[0]

    return uniqueid


def load_preconfig(input):
    """load preconfig data"""

    dataCollection_root = os.path.expanduser("~/eht_dataset")
    dataCollection_json = os.path.join(
        dataCollection_root, input["dataCollection"], f'{input["dataCollection"]}.json'
    )
    with open(dataCollection_json, "r") as f:
        dataCollection = json.load(f)

    # find information
    match = [x for x in dataCollection["datasets"] if input["dataset"] == x["dataset"]]
    #     {
    #         "dataset": "Ma+0.5_w4",
    #         "size": 1000,
    #         "h5_list": "Ma+0.5_w4.txt",
    #         "rho0": "rho0_Ma+0.5.tsv",
    #         "BATCH": "Ma+0.5_w4_BATCH.ALL",
    #         "BATCH_size": 36000
    #     },
    match = match[0]

    return match


def validate_batch_staging(input):
    """input parameters
    -- dict object:
        userName
        experimentName
        dataCollection
        dataset
        parameterFile
    -- return
        experimentId
        jobFile
        expectedOutput
        outputSize
        validate
        BATCH
    """

    v = {}
    v["experimentId"] = get_experimentid(username=input["userName"])

    dataset = input["dataset"]
    parameter = input["parameterFile"]

    # Ma-0.5_w5 -> rho0_Ma-0.5
    # use pre-config
    if dataset.split("_")[0] == parameter.split("_")[1]:
        batchinfo = load_preconfig(input)

    v["expectedOutput"] = batchinfo["BATCH_size"]
    v["BATCH"] = batchinfo["BATCH"]
    # use pre-config
    v["outputSize"] = str(8.8 * v["expectedOutput"] / 1000) + " GB"
    # yes or no
    # if no, need add validateInformation
    v["validate"] = "yes"
    v["validateInformation"] = ""

    workspace = get_workspace()
    stage_json = {**input, **v}
    stage_file = os.path.join(workspace["staging"], f'{v["experimentId"]}.json')
    with open(stage_file, "w") as f:
        json.dump(stage_json, f)

    return stage_json


def getmd5_images(datacollection, dataset, imagelist):
    """get md5 for image list
    return dict{imagename: md5}
    """
    # split name by \n or ,
    import urllib.parse

    imagelist = urllib.parse.unquote(imagelist)
    images = re.split(r"[,\n]", imagelist)
    # print(images, file=sys.stdout)
    # get md5
    dataCollection_root = os.path.expanduser("~/eht_dataset")
    md5file = os.path.join(
        dataCollection_root, datacollection, "md5", f"md5_{dataset}.tsv"
    )
    # print(md5file,file=sys.stdout)
    if not os.path.exists(md5file):
        print("can't find md5 file!", md5file, file=sys.stdout)
        sys.exit()
    # Using a dictionary to store a->b mapping
    a_to_b_mapping = {}
    with open(md5file, "r") as file:
        for line in file:
            a, b = line.split()
            a_to_b_mapping[a] = b

    # Find b values for the desired a values
    results = {a: a_to_b_mapping.get(a, None) for a in images}
    return results


def validate_explorer_staging(input):
    """
    input parameters
        -- dict object:
            userName
            experimentName
            dataCollection
            dataset
            imageList
            parameters
        -- return
            experimentId
            jobFile
            expectedOutput
            outputSize
            validate
            BATCH
    """
    # A sample input
    #     {
    #     "userName": "JunWang",
    #     "experimentName": "433",
    #     "dataCollection": "GRMHD_kharma-v3",
    #     "dataset": "Ma+0.94_w4",
    #     "imageList": "torus.out0.04406.h5\ntorus.out0.04262.h5\ntorus.out0.04967.h5\ntorus.out0.04741.h5\ntorus.out0.04389.h
    # 5\ntorus.out0.04707.h5\ntorus.out0.04788.h5\ntorus.out0.04292.h5\ntorus.out0.04586.h5\ntorus.out0.04843.h5\ntorus.out0.0
    # 4723.h5\ntorus.out0.04667.h5\ntorus.out0.04322.h5\ntorus.out0.04901.h5\ntorus.out0.04094.h5\ntorus.out0.04645.h5\ntorus.
    # out0.04666.h5\ntorus.out0.04971.h5",
    #     "parameters": {
    #   "rr_type": "multiple",
    #   "rr_value": "140,150,160",
    #   "tva_type": "range",
    #   "tva_value": "10:100:10",
    #   "rho_type": "single",
    #   "rho_value": "1.4705331615886175e+18"
    #     }
    # }

    md5s = getmd5_images(input["dataCollection"], input["dataset"], input["imageList"])
    # print(md5s,file=sys.stdout)

    # dict to hold all parameters
    V = {}
    V["ehtimages"] = list(md5s.keys())

    # pass parameters
    para_list = ["rr", "tva", "rho"]
    for para in para_list:
        atype = input["parameters"][f"{para}_type"]
        avalue = input["parameters"][f"{para}_value"]
        value_list = parse_values_bytype(atype, avalue)
        # print(value_list)
        V[para] = value_list

    # generate list of all jobs
    import itertools

    listoflists = [V["ehtimages"], V["rr"], V["tva"], V["rho"]]
    para_combines = list(itertools.product(*listoflists))
    # print(para_combines)
    # print(len(para_combines))

    batchID = get_experimentid(username=input["userName"])
    batchFile = f"{batchID}_BATCH.ALL"

    workspace = get_workspace()
    # generate batchfile
    # osdf:///ospool/uc-shared/public/eht/GRMHD_kharma-v3/Ma+0.5_w4/torus.out0.04011.h5,7f283e457a6d15ca5ef3b5f03e62ba4b,04011,1,10,3.797623637989993e+17
    url_prefix = f'osdf:///ospool/uc-shared/public/eht/{input["dataCollection"]}/{input["dataset"]}'
    batchdata = []
    for job in para_combines:
        inputh5 = job[0]
        inputh5_path = os.path.join(url_prefix, inputh5)
        md5 = md5s[inputh5]
        namepart = inputh5.split(".")[2]
        rr, tva, rho = job[1:]
        batchdata.append([inputh5_path, md5, namepart, rr, tva, rho])

    with open(os.path.join(workspace["staging"], batchFile), "w", newline="") as file:
        import csv

        writer = csv.writer(file, delimiter=",")
        writer.writerows(batchdata)

    # generate stage json
    v_out = {}
    v_out["experimentId"] = batchID
    v_out["expectedOutput"] = len(para_combines)
    v_out["BATCH"] = batchFile
    v_out["imageNumber"] = len(V["ehtimages"])
    outputsize = 8.8 * v_out["expectedOutput"]
    if outputsize < 1000.0:
        v_out["outputSize"] = str(outputsize) + " MB"
    else:
        v_out["outputSize"] = str(outputsize / 1000) + " GB"

    # yes or no
    # if no, need add validateInformation
    v_out["validate"] = "yes"
    v_out["validateInformation"] = ""

    stage_json = {**input, **v_out}
    stage_file = os.path.join(workspace["staging"], f'{v_out["experimentId"]}.json')
    with open(stage_file, "w") as f:
        json.dump(stage_json, f)

    return stage_json


def job_submit_batch(username, experimentid):
    """submit batch job"""

    workspace = get_workspace()
    userfolder = os.path.join(workspace["users"], username)

    job_json = os.path.join(workspace["staging"], f"{experimentid}.json")
    if not os.path.exists(job_json):
        return {"submit": "no", "submitInformation": f"{job_json} is not found!"}

    # extend the job json with submission info
    newinfo = {
        "submit": "yes",
        "submitTime": datetime.now().isoformat(timespec="seconds"),
    }
    append_to_json(job_json, newinfo)
    # copy job_json to user folder,
    jobfolder = experimentid.split("-")[1]
    jobfolder = os.path.join(userfolder, jobfolder)
    if not os.path.exists(jobfolder):
        os.makedirs(jobfolder, exist_ok=True)
    os.system(f"cp {job_json} {jobfolder}")

    # submit the job
    joblog = run_jobscript(experimentid)
    # joblog = "dry run"
    logfile = os.path.join(jobfolder, "submit.log")
    with open(logfile, "w") as f:
        f.write(joblog)

    return {"submit": "yes", "submitInformation": ""}


def job_submit_explorer(username, experimentid):
    """submit explorer job"""

    workspace = get_workspace()
    userfolder = os.path.join(workspace["users"], username)

    job_json = os.path.join(workspace["staging"], f"{experimentid}.json")
    if not os.path.exists(job_json):
        return {"submit": "no", "submitInformation": f"{job_json} is not found!"}

    # test send file to the server
    batch_file = os.path.join(workspace["staging"], f"{experimentid}_BATCH.ALL")
    if os.path.exists(batch_file):
        print("copy batch file.")
        remote_path = "eht_workdirs/staging"
        put_file(batch_file, remote_path)
    else:
        return {"submit": "no", "submitInformation": f"{batch_file} is not found!"}

    # extend the job json with submission info
    newinfo = {
        "submit": "yes",
        "submitTime": datetime.now().isoformat(timespec="seconds"),
    }
    append_to_json(job_json, newinfo)
    # copy job_json to user folder,
    jobfolder = experimentid.split("-")[1]
    jobfolder = os.path.join(userfolder, jobfolder)
    if not os.path.exists(jobfolder):
        os.makedirs(jobfolder, exist_ok=True)
    os.system(f"cp {job_json} {jobfolder}")

    # submit the job
    joblog = run_jobscript(experimentid)
    # joblog = "dry run"
    logfile = os.path.join(jobfolder, "submit.log")
    with open(logfile, "w") as f:
        f.write(joblog)

    return {"submit": "yes", "submitInformation": ""}


def checkexperiment(experimentid):
    """check status of the experiments"""

    username, eid = experimentid.split("-")

    # find the job json file
    workspace = get_workspace()
    jobjson = os.path.join(workspace["users"], username, eid, f"{experimentid}.json")
    with open(jobjson, "r") as f:
        data = json.load(f)

    jobstatus_list = htcondor_status()
    jobstatus = [x for x in jobstatus_list if x["ID"] == experimentid]
    jobstatus = jobstatus[0]

    outputlist = get_outputlist(experimentid)
    outstatus = {}
    outstatus["num"] = len(outputlist)
    outstatus["files"] = outputlist

    newdata = {**{"job": data}, **{"status": jobstatus}, **{"outputs": outstatus}}
    return newdata
