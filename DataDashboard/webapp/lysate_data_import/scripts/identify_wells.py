# imports
import pandas as pd

def identify_wells_in_raw_data(raw_data):

    """
    Get the wells in the experiment by extracting the specific row
    from Timeseries_GFP output, trimming nans and returning
    """
    # get all rows below the metadata
    wells = raw_data.iloc[51,3:].tolist()
    # remove nan
    wells = [x for x in wells if str(x) != 'nan']
    return wells
 