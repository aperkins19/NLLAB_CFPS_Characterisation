#!/bin/bash

# this script automates the raw cfps timeseries fluorescence data pipeline

# delete and reinitalise ./output
rm -r /DataDashboard_app/cfps_data_analysis/output/

mkdir /DataDashboard_app/cfps_data_analysis/output/
mkdir /DataDashboard_app/cfps_data_analysis/output/datasets
mkdir /DataDashboard_app/cfps_data_analysis/output/tmp


# run scripts
python3 "/DataDashboard_app/cfps_data_analysis/scripts/1_preprocessing_tidy.py"

python3 "/DataDashboard_app/cfps_data_analysis/scripts/2_labstep_annotation.py"

