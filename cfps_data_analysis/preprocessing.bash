#!/bin/bash

# this script automates the raw cfps timeseries fluorescence data pipeline

# delete and reinitalise ./output
rm -r output

mkdir output
mkdir output/datasets
mkdir output/tmp


# run scripts
python3 "scripts/1_preprocessing_tidy.py"

