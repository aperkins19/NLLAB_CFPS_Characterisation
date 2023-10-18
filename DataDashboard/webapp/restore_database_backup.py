from utils.mongo_utils import *
import pymongo
from pymongo import MongoClient
import pandas as pd 

# Load csv dataset
data = pd.read_csv('SBSG_Lysate_DataDashboard_Dataset_Full.csv')
print(data)
# Connect to MongoDB
database = mongo_login()
Lysate_Timecourse_collection = database["Lysate_Timecourse"]

data.reset_index(inplace=True)
data_dict = data.to_dict("records")
# Insert collection
Lysate_Timecourse_collection.insert_many(data_dict)