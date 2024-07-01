

import os, sys
from dotenv import load_dotenv
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

def checkuser(username):
    """check user information"""
    userstatus = {}
    userstatus['username'] = username
    history = userhistory(username)
    userstatus['experiments'] = history['experiments']
    userstatus['running'] = 0
    return userstatus

def get_experimentid(username):
    """return an experiment id for a user
        experiment id: 
    """

    import uuid

    longid = uuid.uuid4()
    uniqueid = username[0]+"-"+str(longid).split("-")[0]

    return uniqueid


