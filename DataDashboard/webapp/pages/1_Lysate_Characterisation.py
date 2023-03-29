import streamlit as st
import pandas as pd
import json
import ast

#from utils.lysate_charactisation_utils import *
from utils.bash import *
from utils.labstep_utils import *
from utils.plotting import *

import matplotlib.pyplot as plt
import seaborn as sns

import os

# import paths
paths = json.load(open("/DataDashboard_app/cfps_data_analysis/config/paths.json"))


##### define functions

# reads uploaded excel raw data file and caches in server memory

def read_uploaded_excel(uploaded_file):
    return pd.read_excel(uploaded_file, header=None)

# reads processed csv data file and caches in server memory
def read_processed_csv(path):
    df = pd.read_csv(path)
    return df


# converts stored df to csv
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

#######
# initialise session states for buttons and cached files
if "raw_data_viewer_expanded" not in st.session_state:
    st.session_state["raw_data_viewer_expanded"] = True

if "form_expanded" not in st.session_state:
    st.session_state["form_expanded"] = True

if "processed_data_expanded" not in st.session_state:
    st.session_state["processed_data_expanded"] = True

if "raw_file_cached_status" not in st.session_state:
    st.session_state["raw_file_cached_status"] = False

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

if "data_preprocessing_complete" not in st.session_state:
    st.session_state["data_preprocessing_complete"] = False

if "Calibration_Model_Selected" not in st.session_state:
    st.session_state["Calibration_Model_Selected"] = "None"

if "Calibration_Models_Available" not in st.session_state:
    # initialise the list
    st.session_state["Calibration_Models_Available"] = []
    # read the directory and remove the file extensions
    for model in os.listdir(paths["Calibration"]["Models"]):
        st.session_state["Calibration_Models_Available"] = st.session_state["Calibration_Models_Available"] + [model[:-4]]
    st.session_state["Calibration_Models_Available"] = st.session_state["Calibration_Models_Available"] + ["None"]

if "Lysate_Inventory_List" not in st.session_state:
    # midly hacky way to import the json storing the lysates found in the database
    st.session_state["Lysate_Inventory_List"] = []
    for lysate in list(json.load(open("/DataDashboard_app/webapp/utils/lysate_list.json")).values()):
        st.session_state["Lysate_Inventory_List"] = st.session_state["Lysate_Inventory_List"] + lysate

if "Lysate_selected" not in st.session_state:
    st.session_state["Lysate_selected"] = "None"   

# define callbacks for updating button click session states
def raw_file_cached_status_callback():
    st.session_state["raw_file_cached_status"] = True


def form_callback():

    #### write metadata collected to disk before running preprocessing

    # write well metadata to disk
    # initialise dict
    well_type_dict = {}
    # iterate over saved wells and annotate dict
    for well in st.session_state["Wells"]:
        well_type_dict[well] = {
                        "Well_Type": st.session_state[well],
                        "Lysate_Inventory_Record": st.session_state["Lysate_selected"],
                        "Energy_Solution": "Lysate_Characterisation_1"
                        }
        # delete that individual well session state
        # not working
        del st.session_state[well]

    # save dict to json
    with open(paths["Input"]["Well_Metadata"], 'w') as fp:
        json.dump(well_type_dict, fp)
    # save dict to session state
    st.session_state["Well_Metadata"] = well_type_dict

    # Analysis_Config
    Analysis_Config = {
        "Calibration_Model": st.session_state["Calibration_Model_Selected"]
    }
    ##### write analysis config json here
    with open(paths["Input"]["Analysis_Config"], 'w') as fp:
        json.dump(Analysis_Config, fp)

    # write excel file to server input directory
    raw_upload.to_excel(paths["Input"]["Raw_Data"]+"raw.xlsx", index=False, header=False)

    run_preprocessing_bash_script()


    st.session_state["data_preprocessing_complete"] = True
   
    # sets button states
    st.session_state["form_submitted"] = True
    # minimise forms
    st.session_state["raw_data_viewer_expanded"] = False
    st.session_state["form_expanded"] = False


#### begin page

st.title("Lysate Characterisation")
st.write("text here to explain")

# begin upload section
st.subheader("Upload Raw Data")

# upload excel button
uploaded_file = st.file_uploader(
    "Choose a file",
    accept_multiple_files=False,
    on_change = raw_file_cached_status_callback
    )

# on file cache
if (st.session_state["raw_file_cached_status"]
    and
    uploaded_file is not None):

    # function in utils
    try:
        raw_upload = read_uploaded_excel(uploaded_file)
        st.success("Raw data excel file successfully uploaded.")
    except:
        st.exception("Unable to upload - verify that the file type is .xlsx")

    # instructions text
    st.markdown("Please check that the file looks like it should :mag:")

     # display df
    raw_data_df_expander =  st.expander("Show", expanded= st.session_state["raw_data_viewer_expanded"])
    raw_data_df_expander.write(raw_upload)

    # get the columns by calling 0_identify_wells.py
    columns = subprocess.run(["python3", "/DataDashboard_app/cfps_data_analysis/scripts/0_identify_wells.py"], capture_output=True).stdout
    # decodes the bytes coming from the python print function to ascii characters and then ast decodes to a py list
    # removes Time
    well_list = ast.literal_eval(columns.decode('ascii'))
    well_list.remove("Time")
    st.session_state["Wells"] = well_list

    st.header("Enter Metadata:")

    meta_data_expander = st.expander("Show", expanded = st.session_state["form_expanded"])
    meta_data_form = meta_data_expander.form(key='meta_data_form')
    meta_data_form.subheader("Metadata")

    # lysate selection
    meta_data_form.selectbox(
        "Select the Lysate from the Labstep Inventory:",
        # retrieves the lysates from session state
        (st.session_state["Lysate_Inventory_List"]),
        key = "Lysate_selected"
        )
    # calibration model selection
    calibration_model_selected = meta_data_form.radio(
        "Select a Calibration Model:",
        # retrieves the models from session state
        (st.session_state["Calibration_Models_Available"]),
        key = "Calibration_Model_Selected"
    )

    meta_data_form.subheader("Well Allocation")
    meta_data_form.write("The following wells were observed in your dataset, please designate each as either an experiment or an negative control.")
    meta_data_form.write("The negative controls will be used as a baseline in the analysis.")

    # dyamically produce a form with the correct number of wells
    for well in st.session_state["Wells"]:
        well_cols = meta_data_form.columns(2)
        well_cols[0].write(well)
        well_type_selected = well_cols[1].radio(
            "Well Type",
            ('Experiment', 'Negative_Control'),
            key = well
            )
            
    meta_data_form.form_submit_button("Submit", on_click = form_callback)


    
    # Refresh button
    st.write("Don't see your lysate? Try refreshing the list:")
    
    # button initialisation
    refresh_lysates = st.button("Refresh Lysate List")

    # on call
    if refresh_lysates:
        # wait message
        st.info('Refreshing Lysate List by querying Labstep Database. This may take a few seconds..', icon="ℹ️")
        # execute python script
        s = subprocess.run(["python3", "/DataDashboard_app/webapp/utils/search_lysates_in_api.py"])
        st.success('Lysates refreshed. Reload the page to see them.', icon="✅")
            
    if (
        st.session_state["data_preprocessing_complete"]
        ):

        processed_df = read_processed_csv(paths["Output"]["Datasets"]+"tidy_data_labstep_annotated.csv")
        
        st.subheader("Processed Tidy Dataset:")
        processed_data_expander = st.expander("Show", expanded = st.session_state["processed_data_expanded"])
        processed_data_expander.write(processed_df)

        # convert to csv and download
        csv = convert_df(processed_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name= st.session_state["Lysate_selected"] + '_tidy_annotated_timecourse_data.csv',
            mime='text/csv',
        )

        ## plotting
        # filter data for plotting

        plotting_df = processed_df[["Time", "GFP_uM", "Well"]]
        lysate_characterisation_subplots(processed_df)
