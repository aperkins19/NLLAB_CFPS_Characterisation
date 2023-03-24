"""
# Intro

First script in the data preprocessing that:
* Takes in the raw plate reader csv / excel file and well metadata file
* Returns Tidy Dataset annotated with the metadata.
"""

# imports
import pandas as pd
import json
import os

# functions
from analysis_functions.preprocessing import *

# get paths
paths = json.load(open("/data_pipeline_app/config/paths.json"))

"""
Import:
* Raw data
* well metadata
"""

### import raw data

Input_Directory_Path = paths["Input"]["Raw_Data"]

### list files in directory and use the file that ends in raw.xlsx as Raw_Data_Filename
for filename in os.listdir(Input_Directory_Path):
    if filename[-8:] == "raw.xlsx":
        Raw_Data_Filename = filename

raw_data = pd.read_excel(Input_Directory_Path + Raw_Data_Filename, header=None)

### import well_metadata.json
well_metadata = json.load(open(paths["Input"]["Well_Metadata"]))

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

# Melt wellwise
melted_timecourse_data = MeltDataByExperimentWells(trimmed_timecourse_data, well_metadata)

"""
Metadata Annotation
"""

# annotate the metadata for each well
timecourse_annotated_wells = WellSpecificMetadataAnnotation(melted_timecourse_data, well_metadata)

# annotate the metadata covering the whole experiment
timecourse_annotated = AnnotateExperimentWideMetadata(timecourse_annotated_wells, experiment_metadata_dict)

"""
Save to disk
"""
timecourse_annotated.to_csv(paths["Output"]["Datasets"]+"tidy_data.csv")
