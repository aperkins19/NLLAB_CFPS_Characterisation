import pymongo
from pymongo import MongoClient
import json
import streamlit as st

@st.cache_resource
def mongo_login():

    # get paths
    paths = json.load(open("/DataDashboard_app/paths.json"))
    mongo_auth = json.load(open(paths["API_Authentication"]))

    cluster = MongoClient(mongo_auth["Mongo"]["cntr_name"],
                        mongo_auth["Mongo"]["port"],
                        username=mongo_auth["Mongo"]["MongoLogin"],
                        password=mongo_auth["Mongo"]["MongoPWD"]
                        )

    database = cluster["Database"]

    return database