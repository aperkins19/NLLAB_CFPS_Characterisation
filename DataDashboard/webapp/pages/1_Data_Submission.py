import streamlit as st
import pandas as pd
import json
from pathlib import Path
from utils.labstep_utils import *
from utils.mongo_utils import *

database = mongo_login()
# data processing functions
from lysate_data_import.scripts.identify_wells import *
from lysate_data_import.scripts.preprocessing_tidy import *
from lysate_data_import.scripts.Calibration import *
from lysate_data_import.scripts.zero_gfp import *
from lysate_data_import.scripts.labstep_annotation import *

# dev modules
import os


# import paths
paths = json.load(open("/DataDashboard_app/paths.json"))


# reads uploaded excel raw data file and caches in server memory
def read_uploaded_excel(uploaded_file):
    return pd.read_excel(uploaded_file, header=None)

# converts stored df to csv
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

#######
# initialise session states for buttons and cached files
if "processed_data" not in st.session_state:
    st.session_state["processed_data"] = None


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
    for lysate in list(json.load(open(paths["Lysate_Inventory_List"])).values()):
        st.session_state["Lysate_Inventory_List"] = st.session_state["Lysate_Inventory_List"] + lysate

if "Lab_Member_List" not in st.session_state:
    # midly hacky way to import the json storing the lysates found in the database
    st.session_state["Lab_Member_List"] = json.load(open(paths["Lab_Member_List"])).keys()

if "Lysate_selected" not in st.session_state:
    st.session_state["Lysate_selected"] = "None"

if "Lysate_Owner" not in st.session_state:
    st.session_state["Lysate_Owner"] = "None"

if "negative_control_designated" not in st.session_state:
    st.session_state["negative_control_designated"] = False

if "acceptable_to_submit" not in st.session_state:
    st.session_state["acceptable_to_submit"] = False

if "Lysate_already_submitted" not in st.session_state:
    st.session_state["Lysate_already_submitted"] = False

if "Lysate_successfully_submitted" not in st.session_state:
    st.session_state["Lysate_successfully_submitted"] = False

# define callbacks for updating button click session states
def raw_file_cached_status_callback():
    st.session_state["raw_file_cached_status"] = True


def lysate_refresh_callback():
    # wait message
    st.info('Refreshing Lysate List by querying Labstep Database. This may take a few seconds..', icon="ℹ️")
    # execute python script
    SearchForLysates(paths)
    st.success('Lysates refreshed. Reload the page to see them.', icon="✅")


def submit_to_database_callback():
    # Mongo login
    database = mongo_login()
    Lysate_Timecourse_collection = database["Lysate_Timecourse"]

    #### check that the Lysate_selected is not already in the database.
    database = mongo_login()
    Lysate_Timecourse_collection = database["Lysate_Timecourse"]
    Lysate_Timecourse_pd = pd.DataFrame(list(Lysate_Timecourse_collection.find()))
    # if not empty then check if do the check
    if not (Lysate_Timecourse_pd.empty):
        if (st.session_state["Lysate_selected"] in Lysate_Timecourse_pd["Lysate_Inventory_Record"].unique()):
            st.session_state["Lysate_already_submitted"] = True
        else:
            processed_df.reset_index(drop=True)
            data_dict = processed_df.to_dict("records")
            # Insert collection
            Lysate_Timecourse_collection.insert_many(data_dict)
            st.session_state["Lysate_successfully_submitted"] = True
    else:
        processed_df.reset_index(drop=True)
        data_dict = processed_df.to_dict("records")
        # Insert collection
        Lysate_Timecourse_collection.insert_many(data_dict)
        st.session_state["Lysate_successfully_submitted"] = True




def form_callback():

    #### write metadata collected to disk before running preprocessing
    # write well metadata to disk
    # initialise dict
    well_type_dict = {}
    # iterate over saved wells and annotate dict
    for well in st.session_state["Wells"]:
        # if negative control set session state for preprocessing
        if st.session_state[well] == "Negative_Control":
            st.session_state["negative_control_designated"] = True
        # if ignore - pass
        if st.session_state[well] == "Ignore":
            pass
        well_type_dict[well] = {
                        "Well_Type": st.session_state[well],
                        "Lysate_Inventory_Record": st.session_state["Lysate_selected"],
                        "Energy_Solution": "Lysate_Characterisation_1",
                        "Lysate_Owner": st.session_state["Lab_Member_Selected"]
                        }
        # delete that individual well session state
        # not working
        del st.session_state[well]

    # save dict to session state
    st.session_state["Well_Metadata"] = well_type_dict

    # Analysis_Config
    Analysis_Config = {
        "Calibration_Model": st.session_state["Calibration_Model_Selected"]
    }

    ### execute preprocessing scripts
    # 1. tidy the dataset
    data_in_progress = preprocessing_tidy(raw_upload, well_type_dict, st.session_state["negative_control_designated"], paths)
    # 2. Calibrate signal with selected fluorescent protein model
    data_in_progress = Calibration(data_in_progress, st.session_state["negative_control_designated"], Analysis_Config, paths)
    # 3. Zero GFP signal
    data_in_progress = Zero_GFP(data_in_progress, st.session_state["negative_control_designated"], paths)
    # 4. Annotated with labstep metadata
    processed_df = Annotate_With_Labstep_Metadata(data_in_progress, paths)
    # 5. Cache the processed data to be accessed in the script
    st.session_state["processed_data"] = processed_df

    st.session_state["data_preprocessing_complete"] = True

    # sets button states
    st.session_state["form_submitted"] = True
    # minimise forms
    st.session_state["raw_data_viewer_expanded"] = False
    st.session_state["form_expanded"] = False

    # Data acceptible to submit to database and display submit button
    if (
        st.session_state["form_submitted"] == True
    ):
        st.session_state["acceptable_to_submit"] = True


#### begin page

st.title("Submit New Data")


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

    # get the columns by calling identify_wells_in_raw_data
    well_list = identify_wells_in_raw_data(raw_upload)
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
    
    # lysate owner selection
    meta_data_form.selectbox(
        "Select your name:",
        # retrieves the lysates from session state
        (st.session_state["Lab_Member_List"]),
        key = "Lab_Member_Selected"
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
            "Expression System",
            ("s70_GFP_uM", "T7_GFP_uM", 'Negative_Control', "Ignore"),
            key = well
            )
            
    meta_data_form.form_submit_button("Process", on_click = form_callback)


    
    # Refresh button
    st.write("Don't see your lysate? Try refreshing the list:")
    # button initialisation
    refresh_lysates = st.button("Refresh Lysate List", on_click = lysate_refresh_callback)


            
    if (
        st.session_state["data_preprocessing_complete"]
        ):

        # read the processed data out of the session state as saved in the submit call back
        processed_df = st.session_state["processed_data"]


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

        from utils.plotting import *
        lysate_characterisation_subplots(processed_df, st.session_state["negative_control_designated"], paths)

        if st.session_state["acceptable_to_submit"]:

            submit_to_database_container = st.container()

            submit_to_database_container.header("Submit to database")

            submit_to_database_container.write("Please ensure you have checked over the process data thoroughly and that you are happy with it before submission.")
            submit_to_database_container.write("If you need to resubmit your data due to an error, the prior deletion of your existing data in the database is required.")
            submit_to_database_container.write("Please contact Nadanai or someone with admin privileges to do this.")
            submit_to_database_container.write("This is to prevent the accidental deletion of other people's data.")

            submit_to_database_container.button(
                "Submit",
                key="submit_to_database_button",
                on_click = submit_to_database_callback
                )
            
            if st.session_state["submit_to_database_button"]:
                if st.session_state["Lysate_already_submitted"]:
                    submit_to_database_container.warning("The database already contains data for " + st.session_state["Lysate_selected"] + ". Please ask Nadanai to ask someone with admin privileges to delete it before resubmission.")
                if st.session_state["Lysate_successfully_submitted"]:
                    submit_to_database_container.success("Data for " + st.session_state["Lysate_selected"] + " successfully submitted.")
