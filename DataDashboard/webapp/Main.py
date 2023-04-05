from collections import namedtuple
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import json
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from utils.mongo_utils import *


# get paths
paths = json.load(open("/DataDashboard_app/paths.json"))


st.set_page_config(
    page_title="SBSG Data Science Dashboard",
    page_icon=paths["SBSG_Logo"],
    layout="wide",
)

# ---- initalise paths, functions, callbacks and session states ----

if "cell_culture_metadata_expanded" not in st.session_state:
    st.session_state["cell_culture_metadata_expanded"] = True

if "lysis_metadata_expanded" not in st.session_state:
    st.session_state["lysis_metadata_expanded"] = True

def filter_df_for_plotting(Lysate_Timecourse_pd, expression_system_selected, meta_data_selected, max_time_selected, selected_lysates):

    # delete negative controls
    filtered_df = Lysate_Timecourse_pd[Lysate_Timecourse_pd.Well_Type != "Negative_Control"]
    # expression system
    if expression_system_selected != "All":
        filtered_df = filtered_df[filtered_df.Well_Type == expression_system_selected]
    filtered_df = filtered_df[filtered_df.Time <= max_time_selected]
    filtered_df = filtered_df.loc[filtered_df['Lysate_Inventory_Record'].isin(selected_lysates)]

    meta_data_filtered_df = filtered_df[(['Lysate_Inventory_Record']+ meta_data_selected)]
    meta_data_filtered_df.drop_duplicates(inplace = True)

    return filtered_df, meta_data_filtered_df

def refilter_callback():
    filter_df_for_plotting(Lysate_Timecourse_pd, expression_system_selected, meta_data_selected, max_time_selected, selected_lysates)



# get dataset
database = mongo_login()
Lysate_Timecourse_collection = database["Lysate_Timecourse"]
Lysate_Timecourse_pd = pd.DataFrame(list(Lysate_Timecourse_collection.find()))


## Get data for populating the chart selection options
# lysate list
lysate_list = Lysate_Timecourse_pd["Lysate_Inventory_Record"].unique()
time_list = Lysate_Timecourse_pd["Time"].unique()
min_time = Lysate_Timecourse_pd.loc[:,"Time"].min()
max_time = Lysate_Timecourse_pd.loc[:,"Time"].max()


# ---- manufacturing metadata organisation ----
Lysate_Data_Categories = json.load(open(paths["Input"]["Lysate_Data_Categories"]))

Lysate_Data_Categories_names = []
Pre_Cultures_Data_Categories_name = []
Main_Culture_Data_Categories_name = []
Lysis_Data_Categories_name = []

for key in Lysate_Data_Categories.keys():
    Lysate_Data_Categories_names.append(key)
    if Lysate_Data_Categories[key]["Stage"] == "Cell_Culture_Pre_Cultures":
        Pre_Cultures_Data_Categories_name.append(key)
    elif Lysate_Data_Categories[key]["Stage"] == "Cell_Culture_Main_Culture":
        Main_Culture_Data_Categories_name.append(key)
    elif Lysate_Data_Categories[key]["Stage"] == "Lysis":
        Lysis_Data_Categories_name.append(key)

    Lysate_Data_Categories_types = Lysate_Data_Categories[key]["Type"]


# Sidebar
# Using object notation
st.sidebar.subheader("Timecourse Plotting Metrics")


y_values = st.sidebar.selectbox(
    "Y-Axis:",
    ["GFP_uM", "RFUs"]
)

max_time_selected = st.sidebar.slider(
    "Set time",
    min_value = int(min_time),
    max_value = int(max_time),
    value = int(max_time),
    step=2,
    on_change = refilter_callback,
    format=None,
    disabled=False,
    label_visibility="visible"
    )

st.sidebar.subheader("Filter Data")

expression_system_selected = st.sidebar.selectbox(
    "Select Expression System:",
    ["All", "T7_GFP_uM", "s70_GFP_uM"]
)


selected_lysates = st.sidebar.multiselect(
    "Lysates:",
    lysate_list,
    lysate_list)


#st.sidebar.subheader("Select Manufacture Metadata")
#meta_data_selected = st.sidebar.multiselect(
#    "Select",
#    Lysate_Data_Categories_names,
#    Lysate_Data_Categories_names)
meta_data_selected = Lysate_Data_Categories_names

filtered_df, meta_data_filtered_df = filter_df_for_plotting(Lysate_Timecourse_pd, expression_system_selected, meta_data_selected, max_time_selected, selected_lysates)


## header
header_container = st.container()
header_container.title("SBSG Lysate Dashboard")

 # convert to csv and download
csv = Lysate_Timecourse_pd.to_csv().encode('utf-8')
st.download_button(
    label="Download full dataset as csv",
    data=csv,
    file_name = "SBSG_Lysate_DataDashboard_Dataset_Full.csv",
    mime='text/csv',
)

for lysate in lysate_list:
    # individual lysate slice
    individual_lysate_slice = Lysate_Timecourse_pd[Lysate_Timecourse_pd["Lysate_Inventory_Record"] == lysate]
    # time slice
    time_list = Lysate_Timecourse_pd["Time"].unique()
    for time in time_list:

        time_slice = Lysate_Timecourse_pd[Lysate_Timecourse_pd["Time"] == time]


timecourse_col, endpoint_col = st.columns((1,1))

with timecourse_col:

    st.subheader("Reaction Kinetics")

    fig = plt.figure()

    ax = sns.lineplot(
            data = filtered_df,
            x="Time",
            y=y_values,
            linewidth=1,
            hue = "Lysate_Inventory_Record",
            errorbar = "sd",
            legend = True,
            )

    # calculating plot parameters
    # get the max gfp and round to nearest 0.01
    max_gfp = round(filtered_df[y_values].max(),2)


    time_ticks = []


    ax.set_ylim([0, max_gfp])
    ax.set_yticks([0,(max_gfp/2), max_gfp])
    ax.set_yticklabels([0,(max_gfp/2), max_gfp])
    ax.set_ylabel(y_values)

    ax.set_xticks([0, max_time_selected/2, max_time_selected])
    ax.set_xticklabels([0, max_time_selected/2, max_time_selected])
    ax.set_xlabel("Time (Mins)")

    st.pyplot(fig)

with endpoint_col:

    st.subheader("Endpoint Signal at 300 Minutes")
    
    endpoint_df = filtered_df[filtered_df["Time"] == 300]

    fig = plt.figure()

    ax = sns.barplot(
            data = endpoint_df,
            x="Lysate_Inventory_Record",
            y= y_values,
            hue = "Lysate_Inventory_Record",
            errorbar = "se"
            )

    st.pyplot(fig)



# ---- Manufacturing metadata plotting

# ---- Cell culture

st.subheader("Cell Culture Data:")

cell_culture_metadata_container = st.expander("Show", expanded = st.session_state["cell_culture_metadata_expanded"])

metadata_cols = cell_culture_metadata_container.columns(2)

## cell culture set up
cell_culture_metadata_df = filtered_df.loc[filtered_df['Lysate_Inventory_Record'].isin(selected_lysates)]



# ---- Pre Cultures ----

Pre_Cultures_metadata_df = cell_culture_metadata_df[(["Lysate_Inventory_Record"] + Pre_Cultures_Data_Categories_name)]

Pre_Cultures_metadata_df.drop_duplicates(inplace = True)
Pre_Cultures_metadata_df = pd.melt(
    Pre_Cultures_metadata_df,
    id_vars=["Lysate_Inventory_Record"],
    var_name="Metric",
    value_vars = Pre_Cultures_Data_Categories_name,
    value_name = "Value"
)
fig = px.bar(Pre_Cultures_metadata_df, x="Metric", color="Lysate_Inventory_Record",
            y='Value',
            title="Mini & Midi Culture Metrics",
            barmode='group',
            height=600,
        )

metadata_cols[0].plotly_chart(fig)

# ---- Main Culture ----

Main_Culture_metadata_df = cell_culture_metadata_df[(["Lysate_Inventory_Record"] + Main_Culture_Data_Categories_name)]

Main_Culture_metadata_df.drop_duplicates(inplace = True)
Main_Culture_metadata_df = pd.melt(
    Main_Culture_metadata_df,
    id_vars=["Lysate_Inventory_Record"],
    var_name="Metric",
    value_vars = Main_Culture_Data_Categories_name,
    value_name = "Value"
)
fig = px.bar(Main_Culture_metadata_df, x="Metric", color="Lysate_Inventory_Record",
            y='Value',
            title="Main Culture Metrics",
            barmode='group',
            height=600,
        )

metadata_cols[1].plotly_chart(fig)


# ---- Lysis metadata ----

st.subheader("Lysis Data:")

lysis_metadata_container = st.expander("Show", expanded = st.session_state["lysis_metadata_expanded"])

Lysis_metadata_df = filtered_df[(["Lysate_Inventory_Record"] + Lysis_Data_Categories_name)]
Lysis_metadata_df.drop_duplicates(inplace = True)

lysis_metadata_container.dataframe(Lysis_metadata_df)
