"""
# Intro

First script in the data preprocessing that:
* Takes in the raw plate reader csv / excel file and well metadata file
* Returns Tidy Dataset annotated with the metadata.
"""

# imports
import pandas as pd
import json
import labstep

# functions
from analysis_functions.labstep_utils import *

# get paths
paths = json.load(open("/data_pipeline_app/config/paths.json"))

# get api_authentication
labstep_api_auth = json.load(open(paths["API_Authentication"]))

"""
Login to Labstep API
"""

SBSG_Workspace, user = AuthenticateByUserApiKey(
    email = labstep_api_auth["Labstep_API"]["Email"],
    apiKey = labstep_api_auth["Labstep_API"]["API_Key"],
    workspace_id = labstep_api_auth["Labstep_API"]["Workspace_ID"]
    )

print(user)