# imports
import pandas as pd
import labstep

"""
Data Cleaning and Tidying functions
"""

def AuthenticateByUserApiKey(email, apiKey, workspace_id):
    """
    1. logs in user
    2. returns workspace
    """

    # logs in
    user = labstep.authenticate(
        email,
        apiKey
        )
    
    # gets workspace.
    workspace = user.getWorkspace(
            workspace_id = workspace_id
            )
    
    return workspace, user