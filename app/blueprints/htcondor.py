

import os, sys, json
from dotenv import load_dotenv
from .htcondor_utilities import htcondor_status, run_jobscript, get_outputlist
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
    d_w['workspace'] = workspace
    d_w['staging'] = os.path.join(workspace, "staging")
    d_w['users'] = os.path.join(workspace,"users")
    if not os.path.exists(d_w['staging']):
        os.makedirs(d_w['staging'], exist_ok=True)    
    if not os.path.exists(d_w["users"]):
        os.makedirs(d_w["users"], exist_ok=True)
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
    experiments=[ name for name in os.listdir(userfolder) if os.path.isdir(os.path.join(userfolder, name)) ]
    ex_num = len(experiments)
    return {"experiments": ex_num}

def checkuser(username, simple=False):
    """check user information
        if simple = true, only return 
    """
    userstatus = {}
    userstatus['username'] = username
    history = userhistory(username)
    userstatus['experiments'] = history['experiments']
    userstatus['running'] = 0
    if simple:
        return userstatus
    # other wise return the full records
    userstatus["inqueue"] = ""
    userstatus["recents"] = ""

    # check if there is jobs in htcondor
    joblist = htcondor_status()
    if ((joblist is None) or (len(joblist) == 0)):
        userstatus['running'] = 0
        userstatus['runningExperiments'] = ""
    else:
        jobincondor = [x for x in joblist if username in x['ID']]
        if len(jobincondor) > 0:
            userstatus['running'] = len(jobincondor)
            userstatus['runningExperiments'] = jobincondor
    return userstatus

def get_experimentid(username):
    """return an experiment id for a user
        experiment id: 
    """

    import uuid

    longid = uuid.uuid4()
    uniqueid = username+"-"+str(longid).split("-")[0]

    return uniqueid

def load_preconfig(input):
    """load preconfig data"""

    dataCollection_root = os.path.expanduser("~/eht_dataset")
    dataCollection_json = os.path.join(dataCollection_root, input["dataCollection"],f'{input["dataCollection"]}.json')
    with open(dataCollection_json,"r") as f:
        dataCollection = json.load(f)

    # find information 
    match = [x for x in dataCollection['datasets'] if input['dataset'] == x['dataset']]
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
    """ input parameters
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
    v['experimentId'] = get_experimentid(username = input['userName'])
    
    dataset = input['dataset']
    parameter = input['parameterFile']

    # Ma-0.5_w5 -> rho0_Ma-0.5
    # use pre-config
    if (dataset.split("_")[0] == parameter.split("_")[1]):
        batchinfo = load_preconfig(input)
    
    v['expectedOutput'] = batchinfo['BATCH_size']
    v['BATCH'] = batchinfo['BATCH']
    # use pre-config
    v['outputSize'] = str(8.8 * v['expectedOutput'] /1000) + " GB"
    # yes or no
    # if no, need add validateInformation
    v['validate'] = "yes"
    v['validateInformation'] = ""

    workspace = get_workspace()
    stage_json = {**input, **v}
    stage_file = os.path.join(workspace['staging'],f'{v["experimentId"]}.json')
    with open(stage_file, 'w') as f:
        json.dump(stage_json,f)

    return stage_json

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
    #         "rr_type": "single",
    #         "rrvalue": "10",
    #         "tva_type": "multiple",
    #         "tvavalue": "10,20,30",
    #         "rho_type": "range",
    #         "rhovalue": "10,90,10"
    #     }
    # }

    return

def job_submit_batch(username, experimentid):
    """submit batch job"""

    workspace = get_workspace()
    userfolder = os.path.join(workspace["users"], username)

    job_json = os.path.join(workspace['staging'],f'{experimentid}.json')
    if not os.path.exists(job_json):
        return {"submit":"no","submitInformation":f'{job_json} is not found!'}
                            
    # copy job_json to user folder, 
    jobfolder = experimentid.split("-")[1]
    jobfolder = os.path.join(userfolder, jobfolder)
    if not os.path.exists(jobfolder):
        os.makedirs(jobfolder, exist_ok=True)
    os.system(f"cp {job_json} {jobfolder}")

    # submit the job
    joblog = run_jobscript(experimentid)
    logfile = os.path.join(jobfolder, "submit.log")
    with open(logfile,"w") as f:
        f.write(joblog)

    return {"submit":"yes","submitInformation":""}

def checkexperiment(experimentid):
    """ check status of the experiments"""

    username, eid = experimentid.split("-")

    # find the job json file
    workspace = get_workspace()
    jobjson = os.path.join(workspace['users'],username,eid,f'{experimentid}.json')
    with open(jobjson,'r') as f:
        data = json.load(f)
    
    jobstatus_list = htcondor_status()
    jobstatus = [x for x in jobstatus_list if x['ID']==experimentid]
    jobstatus = jobstatus[0]

    outputlist = get_outputlist(experimentid)
    outstatus = {}
    outstatus['num'] = len(outputlist)
    outstatus['files'] = outputlist

    newdata = {**{"job":data}, **{"status":jobstatus},**{"outputs":outstatus}}
    return newdata