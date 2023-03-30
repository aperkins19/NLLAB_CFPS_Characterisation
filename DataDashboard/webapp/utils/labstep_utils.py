import json
import labstep 
import streamlit as st

@st.cache_data
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

@st.cache_data
def Labstep_Login(paths):

    # get api_authentication
    labstep_api_auth = json.load(open(paths["API_Authentication"]))

    SBSG_Workspace, user = AuthenticateByUserApiKey(
        email = labstep_api_auth["Labstep_API"]["Email"],
        apiKey = labstep_api_auth["Labstep_API"]["API_Key"],
        workspace_id = labstep_api_auth["Labstep_API"]["Workspace_ID"]
        )

    return SBSG_Workspace, user



def SearchForLysates(paths):

    SBSG_Workspace, user = Labstep_Login(paths)

    lysate_inventory_list = []
    lysate_name_prefix = "Lysate_"

    # define the break counter
    # breaks out of loop if 5 consecutive empty records are returned
    break_counter = 0

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
        elif len(lysate) == 0:
            break_counter = break_counter + 1

        if break_counter > 5:
            break

    # on completion
    # stick None on the begining so that it shows up in the selection bar
    lysate_inventory_list.insert(0, "None")
    # reverse list so that the latest shows up first
    lysate_inventory_list.reverse()
    # build dictionary and save as json.
    to_save_json = {
        "Lysate_Inventory_List": lysate_inventory_list
    }
    # write to disk for it to be read in on session start
    with open(paths["Lysate_Inventory_List"], 'w') as fp:
        json.dump(to_save_json, fp)

