"""
# Intro

2nd script in the data preprocessing that:
* Annotates the tidy dataset with metadata from lysate manufacture via the labstep API
* Returns Tidy Dataset annotated with the metadata.
"""

# imports
import pandas as pd
import json
import labstep

# functions
from analysis_functions.labstep_utils import *

# get paths
paths = json.load(open("/DataDashboard_app/cfps_data_analysis/config/paths.json"))

# get api_authentication
labstep_api_auth = json.load(open(paths["API_Authentication"]))

# get lysate data categories
lysate_data_categories = json.load(open(paths["Input"]["Lysate_Data_Categories"]))

"""
Login to Labstep API
"""

SBSG_Workspace, user = AuthenticateByUserApiKey(
    email = labstep_api_auth["Labstep_API"]["Email"],
    apiKey = labstep_api_auth["Labstep_API"]["API_Key"],
    workspace_id = labstep_api_auth["Labstep_API"]["Workspace_ID"]
    )

"""
Import the tidy data
Extract unique lysates
"""

tidy_data = pd.read_csv(paths["Output"]["Datasets"]+"tidy_data.csv")

unique_lysates = tidy_data["Lysate_Inventory_Record"].unique()

"""
Look up the lysates data via the labstep API
"""

# Look up the lysates data via the labstep API and store in list

# initialise list
lysate_data_series_list = []
# interate over the lysates
for lysate in unique_lysates:

    # extract the lysate data and append to list
    # functions in labstep_utils.py
    lysate_data_series_list.append(
        GetLysateData(
            lysate,
            lysate_data_categories,
            SBSG_Workspace
            )
        )

# iterate over the rows in tidy data
new_row_list = []

for i, row in tidy_data.iterrows():

    # iterate over the lysate data series list
    for lysate_data_series in lysate_data_series_list:

        # match the Lysate_Inventory_Records
        if row["Lysate_Inventory_Record"] == lysate_data_series["Lysate_Inventory_Record"]:

            # drop Lysate_Inventory_Record to avoid duplication
            row = row.drop(["Lysate_Inventory_Record"])

            # join the two series, convert to a DF and transpose to make the index the columns
            new_row = pd.concat([row, lysate_data_series], axis = 0).to_frame().transpose()

            # add the 1D DF to the list 
            new_row_list.append(new_row)


# construct the new df
tidy_data_labstep_annotated = pd.concat(new_row_list, axis=0).reset_index(drop=True)

# save to disk
tidy_data_labstep_annotated.to_csv(paths["Output"]["Datasets"]+"tidy_data_labstep_annotated.csv", index=False)
