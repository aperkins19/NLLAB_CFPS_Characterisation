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

def WrangleLabstepDataFields(lysate_data, lysate_data_categories):

    """
    Iterates over the lysate_data_categories to look up data values in the experiement
    associated with the lysate item.
    Extracts and returns data as a pd Series.
    """
    # initialise dict
    retrieved_data_dict = {}

    # iterate over the categories
    for category in lysate_data_categories.keys():

        # extracts the data
        retrieved_data = lysate_data.get(category)

        # If the data field is empty, i.e is 'NoneType' object, then set as None
        if retrieved_data is None:

            # populates the dictionary with None
            retrieved_data_dict[category] = None
        else:
            # if not then extract the data
            # populates the dictionary
            retrieved_data_dict[category] = retrieved_data.getValue()
    # returns series
    return pd.Series(retrieved_data_dict)



def GetLysateData(lysate_name, lysate_data_categories, workspace):

    # retrieve the lysate resource record and access the item.
    # Note, there should be only one item.

    # as this returns a list and there should only be one lysate with that name,
    # a sanity check is performed.
    lysate = workspace.getResources(
    search_query = lysate_name
    )

    if len(lysate) > 1:
        raise Exception("There appears to be more than one lysate in the inventory with the name: " + lysate_name + ". Please resolve before proceeding.")
    elif len(lysate) == 0:
        raise Exception("There appears no lysates in the inventory with the name: " + lysate_name + ". Please resolve before proceeding.")
    else:
        # if theres only one, extract
        lysate = lysate[0]

    # extract the item for that lysate and repeat sanity check.
    lysate = lysate.getItems()
    if len(lysate) > 1:
        raise Exception("There appears to be more than one item associated with " + lysate_name + ". Please resolve before proceeding.")
    elif len(lysate) == 0:
        raise Exception("There appears no items associated with " + lysate_name + ". Please resolve before proceeding.")
    else:
        # if theres only one, extract
        lysate = lysate[0]

    # extract the data associated with that lysate
    lysate_data = lysate.getData()

    # function defined above
    # returns pd Series
    lysate_data_series = WrangleLabstepDataFields(lysate_data, lysate_data_categories)

    # append lysate name to make matching unambigious
    lysate_data_series["Lysate_Inventory_Record"] = lysate_name

    return lysate_data_series

