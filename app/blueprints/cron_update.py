"""
cron_update.py
    -- update job status for all users
"""

import sys
import os
from datetime import datetime
import json
from .htcondor import get_workspace, checkuser
from .htcondor_utilities import run_ssh_cmd
from .utilites import append_to_json


def check_recentjob_status(userfolder, username, jobid, write=False, newinfo={}):
    """check the recent job
    if it has status
    """
    jobfile = os.path.join(userfolder, username, jobid.split("-")[1], f"{jobid}.json")
    if not os.path.exists(jobfile):
        print("jobfile is not found: ", jobfile)
        return None

    if write:
        print("update ", jobid)
        updateinfo = {
            "status": newinfo["jobstatus"],
            "output": newinfo["output"],
            "updateTime": datetime.now().isoformat(timespec="seconds"),
        }
        append_to_json(jobfile, updateinfo)
        return None

    with open(jobfile, "r") as file:
        data = json.load(file)

    if "status" in data:
        v = data
        return v
    else:
        return None


def check_all_status():
    """check job status for all users"""
    workspace = get_workspace()
    if len(workspace["usernames"]) == 0:
        print("no user to check!")
        sys.exit()
    print("workspace", workspace)
    full_status = []
    for user in workspace["usernames"]:
        # get list of submitted jobs from users
        userstatus = checkuser(user)
        recentjobs = userstatus["recents_jobids"]
        print("userstatus", userstatus)
        jobsoneht = check_jobs_eht(user)
        recentjobstatus = []
        # the follow situation needed to be addressed
        # job on the eht, may need to update the status
        # job on the server, no need to update the status
        # job on the server, if no "status", then it need update, otherwise just read out status
        # step 1, check if there is "status", use the status
        # step 2, if now status, try to update it from eht
        # item is jobid
        for item in recentjobs:
            checked_status = check_recentjob_status(workspace["users"], user, item)
            if checked_status is not None:
                recentjobstatus.append(
                    {
                        "jobid": checked_status["experimentId"],
                        "jobstatus": checked_status["status"],
                        "output": checked_status["output"],
                    }
                )
                continue  # skip the check
            if item in jobsoneht:
                newinfo = {}
                if int(jobsoneht[item]) > 0:
                    newinfo = {
                        "jobid": item,
                        "jobstatus": "finished",
                        "output": jobsoneht[item],
                    }
                else:
                    newinfo = {
                        "jobid": item,
                        "jobstatus": "canceled",
                        "output": 0,
                    }
            else:
                newinfo = {
                    "jobid": item,
                    "jobstatus": "unknown",
                    "output": 0,
                }
            recentjobstatus.append(newinfo)
            check_recentjob_status(
                workspace["users"], user, item, write=True, newinfo=newinfo
            )

        updated_status = {**userstatus, **{"recents_jobstatus": recentjobstatus}}
        print(updated_status)
        full_status.append(updated_status)
    return full_status


def update_summary():
    """write a summary file"""
    workspace = get_workspace()["workspace"]
    print(workspace)
    full_status = check_all_status()
    print(full_status)
    summaryfile = os.path.join(workspace, "status_summary.json")
    newinfo = {
        "status": full_status,
        "updateTime": datetime.now().isoformat(timespec="seconds"),
    }

    with open(summaryfile, "w") as file:
        json.dump(newinfo, file)


def check_jobs_eht(username):
    """check jobs on the eht
    {jobid: numberofoutput}
    """
    scriptfolder = "/home/ehtbot/eht_workdirs"
    scriptfile = f"checkjob.sh {username}"
    submitcmd = f"cd {scriptfolder} ; ./{scriptfile}"
    output = run_ssh_cmd(submitcmd)

    outputinfo = output.stdout
    V = {}
    if outputinfo == "":
        print("no job found!")
        return V
    for item in outputinfo.split():
        jobid, output_size = item.split(":")
        V[jobid] = output_size
    return V


def main():
    # ehtjob = check_jobs_eht("haha")
    # print(ehtjob)
    # ehtjob = check_jobs_eht("JunWang")
    # print(ehtjob)
    # check_status()
    update_summary()


if __name__ == "__main__":
    sys.exit(main())
