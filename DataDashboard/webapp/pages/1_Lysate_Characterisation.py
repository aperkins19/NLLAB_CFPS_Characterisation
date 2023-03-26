import streamlit as st
import pandas as pd
import json


#from utils.lysate_charactisation_utils import *
from utils.bash import *
from utils.labstep_utils import *

import os

# import paths
paths = json.load(open("/DataDashboard_app/cfps_data_analysis/config/paths.json"))


##### define functions

# reads uploaded excel raw data file and caches in server memory
@st.cache_data
def read_uploaded_excel(uploaded_file):
    return pd.read_excel(uploaded_file, header=None)

# reads processed csv data file and caches in server memory
@st.cache_data
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
    st.session_state["Calibration_Models_Available"] = st.session_state["Calibration_Models_Available"] = ["None"]
    # read the directory and remove the file extensions
    for model in os.listdir(paths["Calibration"]["Models"]):
        st.session_state["Calibration_Models_Available"] = st.session_state["Calibration_Models_Available"] + [model[:-4]]

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
    # saves form information
    st.session_state["Calibration_Model_Selected"] = calibration_model_selected
    st.session_state["Lysate_selected"] = lysate_selected
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


    st.subheader("Enter Labstep stuff")

    meta_data_form =  st.expander("Show", expanded=st.session_state["form_expanded"])


    with st.form(key='meta_data_form'):
        
        col1, col2 = meta_data_form.columns(2)

        with col1:
            # calibration model selection
            calibration_model_selected = st.selectbox(
                "Select a Calibration Model:",
                # retrieves the models from session state
                (st.session_state["Calibration_Models_Available"])
            )

        with col2:

            # lysate selection

            lysate_selected = st.selectbox(
                "Select the Lysate from the Labstep Inventory:",
                # retrieves the lysates from session state
                (st.session_state["Lysate_Inventory_List"])
                )
            
            # Refresh button
            st.write("Don't see your lysate? Try refreshing the list:")

            # button initialisation
            refresh_lysates = st.button("Refresh Lysate List")

            # on call
            if refresh_lysates:
                # wait message
                st.info('Refreshing Lysate List by querying Labstep Database. This may take a few seconds..', icon="ℹ️")
                # execute python script
                s = subprocess.run(["python3", "DataDashboard_app/webapp/utils/search_lysates_in_api.py"])
                st.success('Lysates refreshed. Reload the page to see them.', icon="✅")

        # wait for both to be selected before displaying submit button
        if calibration_model_selected != "None" and lysate_selected != "None":
            if (
                st.form_submit_button("Submit", on_click = form_callback)
                or
                st.session_state["form_submitted"]
                ):

                #st.write(st.session_state)

                #### write metadata collected to disk before running preprocessing

                # Analysis_Config
                Analysis_Config = {
                    "Calibration_Model": st.session_state["Calibration_Model_Selected"]
                }
                ##### write analysis config json here
                with open(paths["Input"]["Analysis_Config"], 'w') as fp:
                    json.dump(Analysis_Config, fp)


                ##### write well_metadata json here

                # write excel file to server input directory
                raw_upload.to_excel(paths["Input"]["Raw_Data"]+"raw.xlsx", index=False, header=False)

                run_preprocessing_bash_script()

                processed_df = read_processed_csv(paths["Output"]["Datasets"]+"tidy_data_labstep_annotated.csv")
                
                st.write(processed_df)

                st.session_state["data_preprocessing_complete"] = True

    if (
        st.session_state["data_preprocessing_complete"]
        ):

        csv = convert_df(processed_df)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name= st.session_state["Lysate_selected"] + '_tidy_annotated_timecourse_data.csv',
            mime='text/csv',
        )

        st.line_chart(data=processed_df, x="Time", y="GFP_uM", width=0, height=0, use_container_width=True)



