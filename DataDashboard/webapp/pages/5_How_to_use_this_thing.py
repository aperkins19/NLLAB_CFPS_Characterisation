import streamlit as st
from pathlib import Path
import json
# import paths
paths = json.load(open("/DataDashboard_app/paths.json"))

##### define functions

def read_markdown_file(path):
    return Path(path).read_text()


###################################################################
##### all to be wrapped in an imported .py file for refactoring.

###### documentation_expander

#### All documenation is stored in markdown files in static/documentation/Data_Submission
## files are read in read_markdown_file


intro_markdown = read_markdown_file("/DataDashboard_app/webapp/static/documentation/main_documentation_page.md")
st.markdown(intro_markdown, unsafe_allow_html=True)


####################################################################