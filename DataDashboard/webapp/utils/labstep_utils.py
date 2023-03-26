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
def Labstep_Login(labstep_api_auth):

    SBSG_Workspace, user = AuthenticateByUserApiKey(
        email = labstep_api_auth["Labstep_API"]["Email"],
        apiKey = labstep_api_auth["Labstep_API"]["API_Key"],
        workspace_id = labstep_api_auth["Labstep_API"]["Workspace_ID"]
        )

    return SBSG_Workspace, user


#lysate_name_prefix = "Lysate_"
#lysate = workspace.getResources(
#search_query = lysate_name
#)
""" lysate_inventory_list = []
lysate_name_prefix = "Lysate_"
for lysate_number in range(0,100, 1):
    num = str(int(lysate_number) + 1).zfill(3)
    lysate_name = lysate_name_prefix+num

    lysate = SBSG_Workspace.getResources(
    search_query = lysate_name
    )

    if len(lysate) != 0:
        lysate_inventory_list.append(lysate_name)

st.write(lysate_inventory_list) """
