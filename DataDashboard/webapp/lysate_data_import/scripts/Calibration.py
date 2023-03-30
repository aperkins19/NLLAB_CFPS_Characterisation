"""
# Intro

2nd script in the data preprocessing that:
* Takes the selected GFP calibration model and creates a new column called GFP_uM

"""

# imports
import pandas as pd
import json
import os
import pickle
import numpy as np

# Import curve fitting package from scipy
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def Calibration(tidy_data, negative_control_designated,  Analysis_Config, paths):

    # if blank subracted then use that
    if negative_control_designated:
        data_to_calibrate = np.array(tidy_data["RFUs_Baseline_Subtracted"]).reshape(-1,1)
    else:
        data_to_calibrate = np.array(tidy_data["RFUs"]).reshape(-1,1)

    # load selected model
    model_filename = Analysis_Config["Calibration_Model"] +".pkl"
    loaded_model = pickle.load(open(paths["Calibration"]["Models"] + model_filename, 'rb'))


    # get the name of the FP and units.
    # iterate over the string until M is found
    # use index of M to save the name.
    for i, c in enumerate(model_filename):
        if c == "M":
            FP = model_filename[:i+1]

    # determine number of features
    if loaded_model.n_features_in_ > 2:
        # is polynomial
        num_of_features = loaded_model.n_features_in_
        # create the ploy object
        poly = PolynomialFeatures(
            degree=num_of_features,
            include_bias=False
            )
        
        # reshape the RFU column in to numpy array and transform to fit the poly features
        x = poly.fit_transform(
            data_to_calibrate
            )
        
    else:
        x = data_to_calibrate
        
    # Predict and assign to DF under the fluorescent protein and units as given in analysis config.
    tidy_data[FP] = loaded_model.predict(x)

    # label with the model used
    tidy_data["Calibration_Model"] = Analysis_Config["Calibration_Model"]

    return tidy_data

        
