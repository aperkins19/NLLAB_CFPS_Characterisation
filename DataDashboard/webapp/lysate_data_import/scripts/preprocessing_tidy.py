"""
# Intro

First script in the data preprocessing that:
* Takes in the raw plate reader csv / excel file and well metadata file
* Returns Tidy Dataset annotated with the metadata.
"""

# imports
import pandas as pd
import streamlit as st

# functions
from lysate_data_import.scripts.analysis_functions.preprocessing import *

def preprocessing_tidy(raw_data, well_metadata, negative_control_designated, paths):


    """
    Slice and Tidy the raw data and metadata
    First deal with the metadata data contained in the raw data file.
    Then trim the raw data
    """

    ### file metadata

    # slice
    raw_metadata = raw_data.iloc[3:28, 0:2]
    # extract
    experiment_metadata_dict = ExtractExperimentMetadataFromRaw(raw_metadata)


    ### Time course data

    # get all rows below the metadata
    raw_timecourse_data = raw_data.iloc[51:,0:].reset_index(drop=True)

    # trim
    trimmed_timecourse_data = TrimRawTimecourseData(raw_timecourse_data, well_metadata)

    # convert date.time hh:mm:ss to mins
    trimmed_timecourse_data = GetTimeInMinutes(trimmed_timecourse_data)

    # Melt wellwise
    melted_timecourse_data = MeltDataByExperimentWells(trimmed_timecourse_data, well_metadata)
    
    # baseline subtract
    if negative_control_designated == True:
        melted_timecourse_data = baseline_subtract_data(melted_timecourse_data, trimmed_timecourse_data, well_metadata)

    """
    Metadata Annotation
    """

    # annotate the metadata for each well
    timecourse_annotated_wells = WellSpecificMetadataAnnotation(melted_timecourse_data, well_metadata)

    # annotate the metadata covering the whole experiment
    timecourse_annotated = AnnotateExperimentWideMetadata(timecourse_annotated_wells, experiment_metadata_dict)

    return timecourse_annotated