import streamlit as st
import pandas as pd
import json
import os
import subprocess
from subprocess import call
import sys

#from utils.lysate_charactisation_utils import *
from utils.bash import *

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
if "raw_file_cached_status" not in st.session_state:
    st.session_state["raw_file_cached_status"] = False

if "raw_upload_button" not in st.session_state:
    st.session_state["raw_upload_button"] = False

if "run_preprocessing_button" not in st.session_state:
    st.session_state["run_preprocessing_button"] = False

# define callbacks for updating button click session states
def raw_upload_button_callback():
    st.session_state["raw_upload_button"] = True
    # resets run preprocessing session state
    st.session_state["run_preprocessing_button"] = False

def run_preprocessing_button_callback():
    st.session_state["run_preprocessing_button"] = True

def raw_file_cached_status_callback():
    st.session_state["raw_file_cached_status"] = True



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
    raw_data_df_expander =  st.expander("Show", expanded=True)
    raw_data_df_expander.write(raw_upload)

    st.subheader("Enter Labstep stuff")

    meta_data_form =  st.expander("Show", expanded=True)

    meta_data_form.markdown("This text is :red[colored red], and this is **:blue[colored]** and bold.")
    meta_data_form.markdown(":green[$\sqrt{x^2+y^2}=1$] is a Pythagorean identity. :pencil:")

    # display button for save

    if (
        st.button("Upload", on_click = raw_upload_button_callback)
        or
        st.session_state["raw_upload_button"]
        ):


        # write excel file to server input directory
        raw_upload.to_excel(paths["Input"]["Raw_Data"]+"raw.xlsx", index=False, header=False)


        if (
            st.button("Run Preprocessing", on_click = run_preprocessing_button_callback)
            and
            st.session_state["raw_upload_button"]
            ):

            
            run_preprocessing_bash_script()

            processed_df = read_processed_csv(paths["Output"]["Datasets"]+"tidy_data_labstep_annotated.csv")
            
            st.write(processed_df)

            csv = convert_df(processed_df)

            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='large_df.csv',
                mime='text/csv',
            )

            



