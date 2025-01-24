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


def check_all_status():
    """check job status for all users"""
    workspace = get_workspace()
    if len(workspace["usernames"]) == 0:
        print("no user to check!")
        sys.exit()
    # print(workspace["usernames"])
    full_status = []
    for user in workspace["usernames"]:
        # get list of submitted jobs from users
        userstatus = checkuser(user)
        recentjobs = userstatus["recents_jobids"]
        jobsoneht = check_jobs_eht(user)
        recentjobstatus = []
        for item in recentjobs:
            if item in jobsoneht:
                if int(jobsoneht[item]) > 0:
                    recentjobstatus.append(
                        {
                            "jobid": item,
                            "jobstatus": "finished",
                            "output": jobsoneht[item],
                        }
                    )
                else:
                    recentjobstatus.append(
                        {"jobid": item, "jobstatus": "canceled", "output": 0}
                    )
            else:
                recentjobstatus.append(
                    {"jobid": item, "jobstatus": "unknown", "output": 0}
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
