import json
import labstep 
import streamlit as st

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

def Labstep_Login(labstep_api_auth):

    SBSG_Workspace, user = AuthenticateByUserApiKey(
        email = labstep_api_auth["Labstep_API"]["Email"],
        apiKey = labstep_api_auth["Labstep_API"]["API_Key"],
        workspace_id = labstep_api_auth["Labstep_API"]["Workspace_ID"]
        )

    return SBSG_Workspace, user


def SearchForLysates(SBSG_Workspace):

    lysate_inventory_list = []
    lysate_name_prefix = "Lysate_"

    # increment the lysate number
    for lysate_number in range(0,100, 1):
        # add zeros infront
        num = str(int(lysate_number) + 1).zfill(3)
        # build complete name
        lysate_name = lysate_name_prefix+num
        # search api for that lysate name
        lysate = SBSG_Workspace.getResources(
        search_query = lysate_name
        )
        # if is not an empty list, append name to list
        if len(lysate) != 0:
            lysate_inventory_list.append(lysate_name)

    
    # on completion
    # stick None on the begining so that it shows up in the selection bar
    lysate_inventory_list.insert(0, "None")
    # build dictionary and save as json.
    to_save_json = {
        "Lysate_Inventory_List": lysate_inventory_list
    }
    with open(paths["Lysate_Inventory_List"], 'w') as fp:
        json.dump(to_save_json, fp)


# get the api login details
# get paths
paths = json.load(open("/DataDashboard_app/cfps_data_analysis/config/paths.json"))
# get api_authentication
labstep_api_auth = json.load(open(paths["API_Authentication"]))

# login to labstep
SBSG_Workspace, user = Labstep_Login(labstep_api_auth)

SearchForLysates(SBSG_Workspace)