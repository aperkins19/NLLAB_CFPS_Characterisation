import streamlit as st
import pandas as pd
import json

from utils.labstep_utils import *
from utils.mongo_utils import *


# password authentication
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# dev modules
import os

# import paths
paths = json.load(open("/DataDashboard_app/paths.json"))



# initialise database retrieval
database = mongo_login()
Lysate_Timecourse_collection = database["Lysate_Timecourse"]
Lysate_Timecourse_pd = pd.DataFrame(list(Lysate_Timecourse_collection.find()))

# lysate list
lysate_list = Lysate_Timecourse_pd["Lysate_Inventory_Record"].unique()

# initialise
if "Lysates_in_database" not in st.session_state:
    st.session_state["Lysates_in_database"] = lysate_list

# on delete
def delete_form_callback():

    # delete those records from the data base 
    deletion_object = Lysate_Timecourse_collection.delete_many(
        {
        "Lysate_Inventory_Record": st.session_state["Lysate_to_delete_selected"]
        }
        )
    # success message
    st.success(f"Deleted {deletion_object.deleted_count} rows of data where Lysate_Inventory_Record == " + st.session_state["Lysate_to_delete_selected"] + " from the database")

# ------ page --------

st.title("Database Management")

current_database_container = st.container()

# show the current database
current_database_container.header("Current Database")
current_database_container.dataframe(Lysate_Timecourse_pd)


columns = st.columns([1,2])

columns[0].header("Delete Lysate Data")

delete_form = columns[0].form(key='delete_form')

delete_form.selectbox(
    "Select the lysate data to delete from the database:",
    # retrieves the lysates from session state
    (st.session_state["Lysates_in_database"]),
    key = "Lysate_to_delete_selected"
    )

delete_form.form_submit_button("Delete", on_click = delete_form_callback)

