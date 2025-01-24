"""
cron_update.py
    -- update job status for all users
"""

import sys
from .htcondor import get_workspace, userhistory, checkuser


def check_status():
    """check job status for all users"""
    workspace = get_workspace()
    if len(workspace["usernames"]) == 0:
        print("no user to check!")
        sys.exit()
    print(workspace["usernames"])
    for user in workspace["usernames"]:
        # get list of submitted jobs from users
        userstatus = checkuser(user)
        recentjobs = userstatus["recents_jobids"]


def main():
    check_status()


if __name__ == "__main__":
    sys.exit(main())
