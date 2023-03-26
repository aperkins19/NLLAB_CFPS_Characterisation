from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import json

"""
# Welcome to test!
Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:
If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).
In the meantime, below is an example of what you can do with just a few lines of code:
"""
# get paths
paths = json.load(open("/DataDashboard_app/cfps_data_analysis/config/paths.json"))

df = pd.read_csv(paths["Output"]["Datasets"]+"tidy_data.csv")
st.write(df)