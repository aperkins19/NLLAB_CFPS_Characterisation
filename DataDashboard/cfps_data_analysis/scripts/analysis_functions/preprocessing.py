# imports
import pandas as pd
from datetime import datetime
"""
Data Cleaning and Tidying functions
"""

def GetTimeInMinutes(trimmed_timecourse_data):

    # initialise list for populating
    seconds_list = []

    # interate over the rows to get the index
    for i, row in trimmed_timecourse_data.iterrows():
        
        # individually strip the hours, minutes and seconds out of trimmed_timecourse_data["Time"] by using the index i
        # multiply by relevant factor
        # append to list
        seconds_list.append(datetime.strptime(trimmed_timecourse_data["Time"][i], "%H:%M:%S").second + (datetime.strptime(trimmed_timecourse_data["Time"][i], "%H:%M:%S").minute * 60 ) + (datetime.strptime(trimmed_timecourse_data["Time"][i], "%H:%M:%S").hour * 60 * 60))

    # insert the seconds list as Time
    trimmed_timecourse_data["Time"] = seconds_list
    # Divide by 60 to get minutes
    trimmed_timecourse_data["Time"] = trimmed_timecourse_data["Time"] / 60

    # if time starts at 0.05 or above 0, subtract the first time point from all
    if trimmed_timecourse_data["Time"][0] > 0:
        trimmed_timecourse_data["Time"] = trimmed_timecourse_data["Time"] - trimmed_timecourse_data["Time"][0]

    return trimmed_timecourse_data

def ExtractExperimentMetadataFromRaw(raw_metadata):
    """
    Extracts key experiment metadata from the raw data file by hardcoded slicing
    """

    experiment_metadata_dict = {

        # concatenates plate reader name to serial number
        "Plate_Reader_Protocol": raw_metadata.iloc[1,1][-18:-4],
        "Plate_Reader": raw_metadata.iloc[5,1] + "_" + str(raw_metadata.iloc[6,1]),
        # extracts the characters containing the number and converts to float
        "Reaction_Temp_C": float(raw_metadata.iloc[11,1][-4:-2]),
        "Gain": float(raw_metadata.iloc[20,1][-2:]),
        "Date": raw_metadata.iloc[3,1]
    }

    ## sanity check to confirm that the plate reader protocol stated is the same one recorded in the file.
    if experiment_metadata_dict["Plate_Reader_Protocol"] != "Timecourse_GFP":
        raise ValueError("The raw datafile was produced by a different plate reader protocol than Timecourse_GFP.")
    else:
        pass

    return experiment_metadata_dict




def TrimRawTimecourseData(raw_timecourse_data, well_metadata):
    """"
    Trimming raw timecourse data

    Gets rid of all surounding cells in the dataframe
    Sets columns
    Deletes temp column
    """
    ## first find the last row in the column by string matching
    # use it to calculate the last_data_row_index
    for i,row in enumerate(raw_timecourse_data.iloc[:,0]):
        if row == "Results":
            last_data_row_index = i-1

    # slice the raw_data
    trimmed_timecourse_data = raw_timecourse_data.iloc[:last_data_row_index,1:]
    
    # set columns using top row
    trimmed_timecourse_data.columns = trimmed_timecourse_data.iloc[0,:]
    # delete row
    trimmed_timecourse_data = trimmed_timecourse_data.iloc[1:,:].reset_index(drop=True)

    # use the wells in well_metadata.keys() to trim columns
    column_list = ["Time"] + list(well_metadata.keys())
    # trim
    trimmed_timecourse_data = trimmed_timecourse_data[column_list]
    
    return trimmed_timecourse_data


def MeltDataByExperimentWells(trimmed_timecourse_data, well_metadata):
    
    melted_timecourse_data = pd.melt(
        
        # dataset
        trimmed_timecourse_data,
        
        # column not to be changed
        id_vars="Time",
        
        # columns to melt: the well names
        value_vars = list(well_metadata.keys()),
        
        # the new name for the column containing the melted column names
        var_name='Well',

        # The name for the column containing the melted values
        value_name='RFUs'
        )
    
    return melted_timecourse_data


"""
Metadata annotation functions
"""

def WellSpecificMetadataAnnotation(melted_timecourse_data, well_metadata):
    
    """
    Gets wells from well_metadata
    Slices df based on well.
    Populates columns with the metadata from that well
    Reassembles
    """

    # initialise empty df to be populated later.
    timecourse_annotated_wells = pd.DataFrame()

    # iterate over the wells in well_metadata
    for well in list(well_metadata.keys()):

        # slice dataframe to get one well
        well_specific_slice = melted_timecourse_data[melted_timecourse_data["Well"] == well].copy()

        # iterate over the metadata associated with that well and annotate accordingly
        for metadata_key, metadata_value in well_metadata[well].items():
            well_specific_slice.loc[:,metadata_key] = metadata_value


        # add freshly annotated well_specific_slice to the new df
        timecourse_annotated_wells = pd.concat([timecourse_annotated_wells, well_specific_slice])
    
    return timecourse_annotated_wells


def AnnotateExperimentWideMetadata(timecourse_annotated_wells, experiment_metadata_dict):
    """
    Iterates over experiment_metadata_dict
    Populates columns with the metadata
    """
    # iterate over the metadata and annotate accordingly
    for metadata_key, metadata_value in experiment_metadata_dict.items():
        timecourse_annotated_wells.loc[:, metadata_key] = metadata_value

    return timecourse_annotated_wells