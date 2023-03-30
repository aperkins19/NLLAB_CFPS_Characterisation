import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

def lysate_characterisation_subplots(processed_df, negative_control_designated, paths):



    if negative_control_designated == True:
        processed_df = processed_df.loc[processed_df["Well_Type"] != "Negative_Control"]
        y = "GFP_uM"

    else:
        y = "RFUs"

    plotting_df = processed_df[["Time", y, "Well"]]

    #st.write(plotting_df.head())

    st.subheader("View your data")
    tab1, tab2 = st.tabs(["Mean & SEM", "Individual Technical Replicates"])

    with tab1:
        
        fig = plt.figure(figsize=(10, 5))

        fig.suptitle("Mean & SEM of " + st.session_state["Lysate_selected"], fontsize = 18)

        ax = plt.subplot(1, 1, 1)
    
        sns.lineplot(
                data = plotting_df,
                x="Time",
                y=y,
                linewidth=1,
                ax = ax,
                errorbar = "sd",
                legend = None,
                color = "seagreen"
                )

        # calculating plot parameters
        # get the max gfp and round to nearest 0.01
        max_gfp = round(processed_df[y].max(),2)
        max_time = round(processed_df["Time"].max())

        time_ticks = []


        ax.set_ylim([0, max_gfp])
        ax.set_yticks([0,(max_gfp/2), max_gfp])
        ax.set_yticklabels([0,(max_gfp/2), max_gfp], size = "x-large")
        ax.set_ylabel("GFP (μM)", size = "x-large")

        ax.set_xticks([0, max_time/2, max_time])
        ax.set_xticklabels([0, max_time/2, max_time], size = "x-large")
        ax.set_xlabel("Time (Mins)", size = "x-large")
        

        fig.savefig(paths["Output"]["tmp"] + st.session_state["Lysate_selected"] + "_meanplot.png")

        st.pyplot(fig)

        with open(paths["Output"]["tmp"] + st.session_state["Lysate_selected"] + "_meanplot.png", "rb") as file:        
            st.download_button(
                label="Download Mean Plot",
                data = file,
                file_name = st.session_state["Lysate_selected"] + "_meanplot.png",
                mime="image/png"
            )
            

    with tab2:
        fig = plt.figure(figsize=(10, 5))

        fig.suptitle("Individual Technical Replicates of " + st.session_state["Lysate_selected"], fontsize = 18)

        ax = plt.subplot(1, 1, 1)
        sns.lineplot(
                data = plotting_df,
                x="Time",
                y=y,
                hue="Well",
                linewidth=1,
                ax = ax,
                errorbar=None,
                legend = None
                )

        # calculating plot parameters
        # get the max gfp and round to nearest 0.01
        max_gfp = round(processed_df[y].max(),2)
        max_time = round(processed_df["Time"].max())

        time_ticks = []


        ax.set_ylim([0, max_gfp])
        ax.set_yticks([0,(max_gfp/2), max_gfp])
        ax.set_yticklabels([0,(max_gfp/2), max_gfp], size = "x-large")
        ax.set_ylabel("GFP (μM)", size = "x-large")

        ax.set_xticks([0, max_time/2, max_time])
        ax.set_xticklabels([0, max_time/2, max_time], size = "x-large")
        ax.set_xlabel("Time (Mins)", size = "x-large")
        
        fig.savefig(paths["Output"]["tmp"] + st.session_state["Lysate_selected"] + "_individual_replicates_plot.png")

        st.pyplot(fig)
        
        with open(paths["Output"]["tmp"] + st.session_state["Lysate_selected"] + "_individual_replicates_plot.png", "rb") as file:        
            st.download_button(
                label="Download Individual Replicates Plot",
                data = file,
                file_name = st.session_state["Lysate_selected"] + "_individual_replicates_plot.png",
                mime="image/png"
            )
