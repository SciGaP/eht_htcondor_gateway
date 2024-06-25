
def checkuser(username):
    """check user information"""
    userstatus = {}
    userstatus['username'] = username
    userstatus['experiments'] = 10
    userstatus['running'] = 0

    return userstatus