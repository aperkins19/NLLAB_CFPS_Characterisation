"""
# Intro

"Zeros" GFP signal by:

* Finding the lowest GFP signal of each technical replicate for each expression construct.
* Subtracting that lowest signal from each timepoint.

"""

# imports
import pandas as pd
import numpy as np

def Zero_GFP(tidy_data, negative_control_designated, paths):

    """
    First find the min gfp for each replicate and store in min_gfp_dict
    """

    min_gfp_dict = {}

    # get the unique well types
    unique_well_types = list(tidy_data["Well_Type"].unique())

    # slice by well type
    for well_type in unique_well_types:
        well_type_slice = tidy_data[tidy_data["Well_Type"] == well_type].copy()

        # get the unique wells in that slice
        unique_wells = list(well_type_slice["Well"].unique())

        # slice by well
        for well in unique_wells:
            well_slice = well_type_slice[well_type_slice["Well"] == well].copy()

            # if well type is negative control then pass, else store
            if well_type == "Negative_Control":
                pass
            
            else:

                # find lowest GFP
                min_gfp_dict[well] = well_slice["GFP_uM"].min()


    """
    Iterate over the dict and update the specific well GFP values with a their value subracted from the minimum
    """

    for well, min_gfp in min_gfp_dict.items():
        tidy_data.loc[tidy_data["Well"] == well, "GFP_uM"] = tidy_data.loc[tidy_data["Well"] == well, "GFP_uM"] - min_gfp


    return tidy_data