from pymongo import *
import pandas as pd
import json

MONGODB_HOST = 'mongodb+srv://Capstone:ProfWade2023@cluster0.9c4phbt.mongodb.net/?retryWrites=true&w=majority'
MONGODB_ClIENT = 27017
csvName = 'data/CHILD_Working_DB_v2 - Sheet1.csv'

# possibly more efficient method of insertion
def csv_to_dict_insert(db_host, db_client, filename):
    client = MongoClient(MONGODB_HOST, MONGODB_ClIENT)

    db = client["IntelligentChild"]

    collection_name = db["Resources"]

    df = pd.read_csv(filename)

    cols = ["Title", "Organization", "Role Rel'ps", "Description", "City"]

    # creates a new description field containing above columns
    df = preprocess(df, cols)

    result = df.to_dict(orient='records')
    collection_name.drop()
    collection_name.insert_many(result)

def preprocess(df, cols):
    # removes NaN so the preprocessing function works
    df = df.fillna('')
    df["PDescription"] = df[cols].agg('-'.join, axis=1)
    return df

csv_to_dict_insert(MONGODB_HOST, MONGODB_ClIENT, csvName)