import streamlit as st
import subprocess



""""
bash script for preprocessing
"""
def run_preprocessing_bash_script():

    p = subprocess.run(
                ["/bin/bash", "DataDashboard_app/cfps_data_analysis/preprocessing.bash"],
                executable="/bin/bash"
    )
    return st.success('Data Preprocessing complete.', icon="✅")

