

import os, sys, json
from dotenv import load_dotenv
from .htcondor_utilities import htcondor_status
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
    experiments = [x for x in os.listdir(userfolder) if "experiment" in x]
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

def job_submit_batch(username, experimentid):
    """submit batch job"""

    workspace = get_workspace()
    userfolder = os.path.join(workspace["users"], username)

    job_json = os.path.join(workspace['staging'],f'{experimentid}.json')
    if not os.path.exists(job_json):
        return {"submit":"no","submitInformation":f'{job_json} is not found!'}
                            
    # copy job_json to user folder
    # submit the job
    
    return {"submit":"yes","submitInformation":""}

def checkexperiment(experimentid):
    """ check status of the experiments"""

    username, eid = experimentid.split("-")

    # find the job json file
    workspace = get_workspace()
    jobjson = os.path.join(workspace['users'],username,eid,f'{experimentid}.json')
    with open(jobjson,'r') as f:
        data = json.load(f)
    
    jobstatus = htcondor_status()

    newdata = {**{"job":data}, **{"status":jobstatus}}
    return newdata