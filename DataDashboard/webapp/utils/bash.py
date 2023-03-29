import streamlit as st
import subprocess



""""
bash script for preprocessing
"""
def run_preprocessing_bash_script():

    exit_code = subprocess.call("/DataDashboard_app/cfps_data_analysis/preprocessing.sh")
    
    if exit_code == 0:
        st.success('Data Preprocessing complete.', icon="✅")
    else:
        st.exception("Data Preprocessing Failed")

