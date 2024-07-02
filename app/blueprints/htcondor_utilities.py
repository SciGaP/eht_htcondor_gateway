"""
    htcondor_utilities.py
        -- assistant function to connect to osg node
        -- job submission
        -- job status report
    
    configuration:
        .env contains ssh connection parameters
            put it the values for the following keys:
                - userA,sshA,keyA,passA
                - userB,sshB,keyB,passB
"""

import os
import sys

from dotenv import load_dotenv
from fabric import Connection
import re
from datetime import datetime

# load server setup
load_dotenv()

def get_connection():
    """get the parameters for the connection"""

    gateway = {
        "host": os.getenv("sshA"),
        "user": os.getenv("userA"),
        "connect_kwargs": {
            "key_filename": os.path.expanduser(os.getenv("keyA")),
            "passphrase": os.getenv("passA"),
        },
    }

    target_host = {
        "host": os.getenv("sshB"),
        "user": os.getenv("userB"),
        "connect_kwargs": {
            "key_filename": os.path.expanduser(os.getenv("keyB")),
            "passphrase": os.getenv("passB"),
        },
    }

    return [gateway, target_host]

def run_ssh_cmd(cmd_str):
    """run a command in ssh"""

    gateway, target_host = get_connection()

    # Connect to the target host via the gateway
    with Connection(**target_host, gateway=Connection(**gateway)) as conn:
        result = conn.run(cmd_str, hide=True)
        return result

def get_file(remote_path, local_path):
    """download file from the sever"""
    gateway, target_host = get_connection()

    with Connection(**target_host, gateway=Connection(**gateway)) as conn:
        result = conn.get(remote_path, local_path)
        return result
    

def extract_numbers_from_line(line):
    """find all the numbers from line"""
    numbers = re.findall(r"\d+", line)
    return list(map(int, numbers))


def htcondor_status():
    """query the htcondor status
    
    -- Schedd: ospool-eht.chtc.wisc.edu : <128.105.68.10:9618?... @ 07/02/24 09:09:15
    OWNER  BATCH_NAME                SUBMITTED   DONE   RUN    IDLE   HOLD  TOTAL JOB_IDS
    ehtbot straycatcoder-3cbf15ae   7/2  09:03      _   1153  34841      6  36000 87.0 ... 98.2999

    Total for query: 36000 jobs; 0 completed, 0 removed, 34841 idle, 1153 running, 6 held, 0 suspended
    Total for ehtbot: 36000 jobs; 0 completed, 0 removed, 34841 idle, 1153 running, 6 held, 0 suspended
    Total for all users: 36000 jobs; 0 completed, 0 removed, 34841 idle, 1153 running, 6 held, 0 suspended
    
    """

    condor_q = run_ssh_cmd("condor_q")
    condor_q = condor_q.stdout

    print(condor_q)
    # find header
    header = [x for x in condor_q.split("\n") if "OWNER" in x.strip()]
    header = header[0]
    holdflag = False
    if "HOLD" in header:
        holdflag = True

    ehtbot_status = [x for x in condor_q.split("\n") if x.strip().startswith('ehtbot')]
    if len(ehtbot_status) == 0:
        return None
    ehtbot_status = ehtbot_status[0]
    raw = ehtbot_status.replace("_","0").split()
    print(raw)
    # ['ehtbot', 'straycatcoder-3cbf15ae', '7/2', '09:03', '0', '1757', '34243', '36000', '87.0', '...', '98.2999']
    jobid = raw[1]
    jobtime = raw[2]+" " + raw[3]
    jobdone = int(raw[4])
    jobrun = int(raw[5])
    jobidle = int(raw[6])
    if holdflag:
        jobhold = int(raw[7])
        jobtotal = int(raw[8])
    else:
        jobhold = 0
        jobtotal = int(raw[7])

    status = {}
    status['ID'] = jobid
    status['SUBMITTED'] = jobtime
    status['DONE'] = jobdone
    status['RUN'] = jobrun
    status['IDLE'] = jobidle
    status['HOLD'] = jobhold
    status['TOTAL'] = jobtotal
    
    return status

    # this is for the remaining jobs
    # status_line = [x for x in condor_q.stdout.split("\n") if "Total for query" in x]
    # if status_line == []:
    #     print("job status is not available, try it later.")
    #     return
    # # "Total for query: 50 jobs; 40 completed, 2 removed, 3 idle, 2 running, 2 held, 1 suspended"
    # status_line = status_line[0]
    # numbers = extract_numbers_from_line(status_line)
    # keys = ["jobs", "completed", "removed", "idle", "running", "held", "suspended"]
    # status = dict(zip(keys, numbers))
    #return status

def check_htcondor_status():
    """visualize htcondor_status"""

    # get status 
    status = htcondor_status()
    if status == None:
        print("no job is running!")
        return 
    print(f"JobID: {status['ID']}, Total: {status['TOTAL']}, Submit Time: {status['SUBMITTED']}")
    
    now = datetime.now()
    current_time = now.strftime("%m/%d %H:%M")
    progress = status['DONE']/status['TOTAL']*100.0
    print(f"status report {progress:.2f}% done @ {current_time}")
    print(f"Done - {status['DONE']}: ","*"*status['DONE'])
    print(f"Run - {status['RUN']}: ", "*"*status['RUN'])
    print(f"Idle - {status['IDLE']}: ", "*"*status['IDLE'])
    print(f"Hold - {status['HOLD']}: ", "*"*status['HOLD'])
    

def check_output():
    """check the output file"""

    outputdir = os.getenv("output")
    cmd = f"ls {outputdir}"
    response = run_ssh_cmd(cmd)
    h5list = response.stdout.split("\n")
    relist = [x for x in h5list if ".h5" in x]
    #print(relist)
    return relist

def get_output(outputfile, localpath="."):
    """download output file"""

    outputdir = os.getenv("output")
    remotefile = os.path.join(outputdir, outputfile)
    localfile = os.path.join(localpath,outputfile)
    response = get_file(remotefile,localfile)
    print(response.local)
    print("File transfer successful!")

def check_errorlog():
    """check the error log"""
    logdir = os.getenv("log")
    cmd = f"ls {logdir}"
    response = run_ssh_cmd(cmd)
    errorlist = response.stdout.split("\n")
    relist = [x for x in errorlist if ".err" in x]
    return relist

def job_submission(paras,dryrun=False):
    """submit a job with paras"""

    from jobsubmission.eht_submit import alljobs_dict
    all_jobs =alljobs_dict(paras)

    if dryrun:
        print("total jobs: ", len(all_jobs))
        print("ready to submit")
        return
    
    script = os.getenv("script")
    ehtdata = paras['ehtdata']
    rr = paras['rr']
    tva = paras['tva']
    rdm = paras['rdm']
    submitcmd = f"{script} {ehtdata} {rr} {tva} {rdm}"
    output = run_ssh_cmd(submitcmd)
    print(output.stdout)

    return

def run_testjob(submit=False):
    """a test case"""
    job_paras = {}    
    job_paras["ehtdata"] = "torus.out0.05992.h5,torus.out0.05993.h5,torus.out0.05994.h5,torus.out0.05995.h5,torus.out0.05996.h5"
    job_paras["rr"] = "10:100:10"
    job_paras["tva"] = "30,50,60,70,80,90"
    job_paras["rdm"] = "4.266338570441294e+17"

    print("A test case with the following parameters:")
    print("Ehtdata: ", job_paras["ehtdata"])
    print("Rhigh-Ratio: ", job_paras["rr"])
    print("Theta-Viewing-Angle: ", job_paras["tva"])
    print("Rho0-Density-Normalization: ", job_paras["rdm"])

    dryrun = True
    if submit:
        dryrun = False
    job_submission(job_paras, dryrun=dryrun)

def main():
    """test the routines"""
    output = run_ssh_cmd("hostname")
    print("stdout:", output.stdout)
    print("stderr:", output.stderr)

    status = htcondor_status()
    print(status)

if __name__ == "__main__":
    sys.exit(main())
