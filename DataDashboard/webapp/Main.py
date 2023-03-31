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

st.set_page_config(
    page_title="SBSG Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

if "manufacture_metadata_expanded" not in st.session_state:
    st.session_state["manufacture_metadata_expanded"] = True

def filter_df_for_plotting(Lysate_Timecourse_pd, meta_data_selected, max_time_selected, selected_lysates):

    filtered_df = Lysate_Timecourse_pd[Lysate_Timecourse_pd.Well_Type != "Negative_Control"]
    filtered_df = filtered_df[filtered_df.Time <= max_time_selected]
    filtered_df = filtered_df.loc[filtered_df['Lysate_Inventory_Record'].isin(selected_lysates)]

    meta_data_filtered_df = filtered_df[(['Lysate_Inventory_Record']+ meta_data_selected)]
    meta_data_filtered_df.drop_duplicates(inplace = True)

    return filtered_df, meta_data_filtered_df

def refilter_callback():
    filter_df_for_plotting(Lysate_Timecourse_pd, meta_data_selected, max_time_selected, selected_lysates)


# get paths
paths = json.load(open("/DataDashboard_app/paths.json"))

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

Lysate_Data_Categories = json.load(open(paths["Input"]["Lysate_Data_Categories"]))
Lysate_Data_Categories_names = []
Cell_Culture_Data_Categories_name = []
for key in Lysate_Data_Categories.keys():
    Lysate_Data_Categories_names.append(key)
    if Lysate_Data_Categories[key]["Stage"] == "Cell_Culture":
        Cell_Culture_Data_Categories_name.append(key)

    Lysate_Data_Categories_types = Lysate_Data_Categories[key]["Type"]


# Sidebar
# Using object notation
st.sidebar.subheader("Select Data")

y_values = st.sidebar.selectbox(
    "Y-Axis:",
    ["GFP_uM", "RFUs"]
)
selected_lysates = st.sidebar.multiselect(
    "Lysates:",
    lysate_list,
    lysate_list)

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

st.sidebar.subheader("Select Manufacture Metadata")
meta_data_selected = st.sidebar.multiselect(
    "Select",
    Lysate_Data_Categories_names,
    Lysate_Data_Categories_names)

filtered_df, meta_data_filtered_df = filter_df_for_plotting(Lysate_Timecourse_pd, meta_data_selected, max_time_selected, selected_lysates)


## header
header_container = st.container()
header_container.header("SBSG Lysate Dashboard")

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
    
    endpoint_df = Lysate_Timecourse_pd[Lysate_Timecourse_pd["Time"] == 300]

    fig = plt.figure()

    ax = sns.barplot(
            data = endpoint_df,
            x="Lysate_Inventory_Record",
            y= y_values,
            hue = "Lysate_Inventory_Record",
            errorbar = "se"
            )

    st.pyplot(fig)


st.subheader("Manufacturing Data:")

manufacture_metadata_container = st.expander("Show", expanded = st.session_state["manufacture_metadata_expanded"])

#manufacture_metadata_container.dataframe(meta_data_filtered_df)

metadata_cols = manufacture_metadata_container.columns(2)

## cell culture set up
cell_culture_metadata_df = Lysate_Timecourse_pd.loc[Lysate_Timecourse_pd['Lysate_Inventory_Record'].isin(selected_lysates)]
cell_culture_metadata_df = cell_culture_metadata_df[(["Lysate_Inventory_Record"] + Cell_Culture_Data_Categories_name)]
cell_culture_metadata_df.drop_duplicates(inplace = True)
cell_culture_metadata_df = pd.melt(
    cell_culture_metadata_df,
    id_vars=["Lysate_Inventory_Record"],
    var_name="Metric",
    value_vars = Cell_Culture_Data_Categories_name,
    value_name = "Value"
)
fig = px.bar(cell_culture_metadata_df, x="Metric", color="Lysate_Inventory_Record",
            y='Value',
            title="Cell Culture Metrics",
            barmode='group',
            height=600,
        facet_row="Lysate_Inventory_Record"
        )




metadata_cols[0].plotly_chart(fig)
metadata_cols[1].write("test")
