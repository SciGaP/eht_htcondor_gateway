
import os, sys
from dotenv import load_dotenv
load_dotenv()
workspace = os.path.expanduser(os.getenv("workspace"))

def inituser(username,userfolder):
    """init user folder in workspace"""
    os.makedirs(userfolder, exist_ok=True)

def userhistory(username):
    """check job history of a user"""

    userfolder = os.path.join(workspace,username)
    if not os.path.exists(userfolder):
        inituser(username,userfolder)
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


