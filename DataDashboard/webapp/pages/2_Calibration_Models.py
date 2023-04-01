import streamlit as st
import pandas as pd
import json
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np

# Import curve fitting package from scipy
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# import paths
paths = json.load(open("/DataDashboard_app/paths.json"))

##### define functions

def Generate_Calibration_Plot(model_name, calibration_data_df, calibration_model):

    FP = calibration_data_df["FP"][0]

    data_to_calibrate = np.array(calibration_data_df["RFU"]).reshape(-1,1)
    y = np.array(calibration_data_df["Concentration_uM"]).reshape(-1,1)

    # determine number of features
    if calibration_model.n_features_in_ > 2:
        # is polynomial
        num_of_features = calibration_model.n_features_in_
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
    y_predicted = calibration_model.predict(x)

    fig = plt.figure(figsize=(10, 5))

    fig.suptitle(model_name, fontsize = 18)


    plt.scatter(data_to_calibrate, y)
    plt.plot(data_to_calibrate, y_predicted, color='purple')

    # calculating plot parameters
    # get the max gfp and round to nearest 0.01

    plt.ylabel(FP + " (μM)", size = "x-large")
    plt.xlabel("RFUs", size = "x-large")
    
    st.pyplot(fig)


# ---- start Page -----

# Title

st.title("Calibration Models")
st.write("The models below contain all the information required to choose a model to calibrate your raw data.")
st.write("Please pay attention to which gain setting and plate reader was used.")

for filename in os.listdir(paths["Calibration"]["Data"]):
    f = os.path.join(paths["Calibration"]["Data"], filename)

    # Model Name
    model_name = filename[:-5]

    # import data
    calibration_data_df = pd.read_excel(f)
    
    # import model
    model_filename = model_name+".pkl"
    calibration_model = pickle.load(open(paths["Calibration"]["Models"] + model_filename, 'rb'))

    # assign model name
    calibration_data_df["Model_Name"] = model_name

    # generate the plot
    Generate_Calibration_Plot(model_name, calibration_data_df, calibration_model)
    
    # write gain and plate reader
    st.write("Plate_Reader: " + calibration_data_df["Plate_Reader"][0])
    st.write("Gain: " + str(calibration_data_df["Gain"][0]))


#loaded_model = pickle.load(open(paths["Calibration"]["Models"] + model_filename, 'rb'))