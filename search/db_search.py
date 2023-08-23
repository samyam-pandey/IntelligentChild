import torch
torch.set_num_threads(1)
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
from flask import Flask
from flask import render_template
from flask import request
import urllib.parse

#Initialization
app = Flask(__name__)

# Executes when first user accesses site
@app.before_first_request
def connection_and_setup():
    MONGODB_HOST = 'mongodb+srv://Capstone:ProfWade2023@cluster0.9c4phbt.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(MONGODB_HOST)
    db = client["IntelligentChild"]
    global collection_name
    collection_name = db["Preprocess"]
    global embedder
    embedder = SentenceTransformer('../models/model1')

    resources = collection_name.find({}, {"Organization": 1, "Description": 1, "Email": 1, "Work Phone": 1, "PDescription": 1})
    global corpus
    corpus = [resource["PDescription"] for resource in resources]

    print("******BEGINNING PREPROCESS*******")
    embeddings = embedder.encode(corpus, convert_to_tensor=True)
    global encoding_dict
    encoding_dict = {}
    encoding_dict["Encodings"] = embeddings
    print("*******END PREPROCESS********")

#connection_and_setup()

# core search algorithm separated out for testing
def core_search(query, embedder, corpus, encoding_dict):
    crossEncoderItems = []
    crossEncoderScoresDict = {}
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, encoding_dict["Encodings"])[0]
    top_k = min(5, len(corpus))
    top_results = torch.topk(cos_scores, k=top_k)

    for score, idx in zip(top_results[0], top_results[1]):
        crossEncoderItems.append(tuple([query, corpus[idx]]))
        crossEncoderScoresDict[corpus[idx]] = score
    
    return crossEncoderItems, crossEncoderScoresDict

def grab_info(crossEncoderItems, crossEncoderScoresDict, collection_name):
    winningResource = crossEncoderItems[0][1]
    secondResource = crossEncoderItems[1][1]
    thirdResource = crossEncoderItems[2][1]
    fourthResource = crossEncoderItems[3][1]
    fifthResource = crossEncoderItems[4][1]

    winningPDescription = collection_name.find_one({"PDescription": winningResource})
    secondPDescription = collection_name.find_one({"PDescription": secondResource})
    thirdPDescription = collection_name.find_one({"PDescription": thirdResource})
    fourthPDescription = collection_name.find_one({"PDescription": fourthResource})
    fifthPDescription = collection_name.find_one({"PDescription": fifthResource})

    winningName = winningPDescription["Organization"]
    secondName = secondPDescription["Organization"]
    thirdName = thirdPDescription["Organization"]
    fourthName = fourthPDescription["Organization"]
    fifthName = fifthPDescription["Organization"]

    winningDescription = winningPDescription["Description"]
    secondDescription = secondPDescription["Description"]
    thirdDescription = thirdPDescription["Description"]
    fourthDescription = fourthPDescription["Description"]
    fifthDescription = fifthPDescription["Description"]

    winningWorkPhone = winningPDescription["Work Phone"]
    secondWorkPhone = secondPDescription["Work Phone"]
    thirdWorkPhone = thirdPDescription["Work Phone"]
    fourthWorkPhone = fourthPDescription["Work Phone"]
    fifthWorkPhone = fifthPDescription["Work Phone"]

    winningConfidence = crossEncoderScoresDict[winningResource]
    secondConfidence = crossEncoderScoresDict[secondResource]
    thirdConfidence = crossEncoderScoresDict[thirdResource]
    fourthConfidence = crossEncoderScoresDict[fourthResource]
    fifthConfidence = crossEncoderScoresDict[fifthResource]
    return winningPDescription, secondPDescription, thirdPDescription, fourthPDescription, fifthPDescription, winningName, secondName, thirdName, fourthName, fifthName, winningDescription, secondDescription, thirdDescription, fourthDescription, fifthDescription, winningWorkPhone, secondWorkPhone, thirdWorkPhone, fourthWorkPhone, fifthWorkPhone, winningConfidence, secondConfidence, thirdConfidence, fourthConfidence, fifthConfidence
    
# algorithm to create address links separated out for testing
def create_addresses(winningPDescription, secondPDescription, thirdPDescription, fourthPDescription, fifthPDescription):
    winningAddress = ""
    winningAddressUnencoded = "No location provided"
    if winningPDescription["ZIP"] != "":
        winningAddress = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(winningPDescription["Street Address"] + ", " + winningPDescription["City"] + ", " + winningPDescription["State"] + " " + str(int(winningPDescription["ZIP"])))
        winningAddressUnencoded = winningPDescription["Street Address"] + ", " + winningPDescription["City"] + ", " + winningPDescription["State"] + " " + str(int(winningPDescription["ZIP"]))
        if winningAddressUnencoded[0] == ',' and winningAddressUnencoded[2] == ',':
            winningAddress = ""
            winningAddressUnencoded = "No location provided"
        elif winningAddressUnencoded[0] == ',':
            winningAddressUnencoded = winningPDescription["City"] + ", " + winningPDescription["State"] + " " + str(int(winningPDescription["ZIP"]))
    secondAddress = ""
    secondAddressUnencoded = "No location provided"
    if secondPDescription["ZIP"] != "":
        secondAddress = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(secondPDescription["Street Address"] + ", " + secondPDescription["City"] + ", " + secondPDescription["State"] + " " + str(int(secondPDescription["ZIP"])))
        secondAddressUnencoded = secondPDescription["Street Address"] + ", " + secondPDescription["City"] + ", " + secondPDescription["State"] + " " + str(int(secondPDescription["ZIP"]))
        if secondAddressUnencoded[0] == ',' and secondAddressUnencoded[2] == ',':
            secondAddress = ""
            secondAddressUnencoded = "No location provided"
        elif secondAddressUnencoded[0] == ',':
            secondAddressUnencoded = secondPDescription["City"] + ", " + secondPDescription["State"] + " " + str(int(secondPDescription["ZIP"]))
    thirdAddress = ""
    thirdAddressUnencoded = "No location provided"
    if thirdPDescription["ZIP"] != "":
        thirdAddress = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(thirdPDescription["Street Address"] + ", " + thirdPDescription["City"] + ", " + thirdPDescription["State"] + " " + str(int(thirdPDescription["ZIP"])))
        thirdAddressUnencoded = thirdPDescription["Street Address"] + ", " + thirdPDescription["City"] + ", " + thirdPDescription["State"] + " " + str(int(thirdPDescription["ZIP"]))
        if thirdAddressUnencoded[0] == ',' and thirdAddressUnencoded[2] == ',':
            thirdAddress = ""
            thirdAddressUnencoded = "No location provided"
        elif thirdAddressUnencoded[0] == ',':
            thirdAddressUnencoded = thirdPDescription["City"] + ", " + thirdPDescription["State"] + " " + str(int(thirdPDescription["ZIP"]))
    fourthAddress = ""
    fourthAddressUnencoded = "No location provided"
    if fourthPDescription["ZIP"] != "":
        fourthAddress = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(fourthPDescription["Street Address"] + ", " + fourthPDescription["City"] + ", " + fourthPDescription["State"] + " " + str(int(fourthPDescription["ZIP"])))
        fourthAddressUnencoded = fourthPDescription["Street Address"] + ", " + fourthPDescription["City"] + ", " + fourthPDescription["State"] + " " + str(int(fourthPDescription["ZIP"]))
        if fourthAddressUnencoded[0] == ',' and fourthAddressUnencoded[2] == ',':
            fourthAddress = ""
            fourthAddressUnencoded = "No location provided"
        elif fourthAddressUnencoded[0] == ',':
            fourthAddressUnencoded = fourthPDescription["City"] + ", " + fourthPDescription["State"] + " " + str(int(fourthPDescription["ZIP"]))
    fifthAddress = ""
    fifthAddressUnencoded = "No location provided"
    if fifthPDescription["ZIP"] != "":
        fifthAddress = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(fifthPDescription["Street Address"] + ", " + fifthPDescription["City"] + ", " + fifthPDescription["State"] + " " + str(int(fifthPDescription["ZIP"])))
        fifthAddressUnencoded = fifthPDescription["Street Address"] + ", " + fifthPDescription["City"] + ", " + fifthPDescription["State"] + " " + str(int(fifthPDescription["ZIP"]))
        if fifthAddressUnencoded[0] == ',' and fifthAddressUnencoded[2] == ',':
            fifthAddress = ""
            fifthAddressUnencoded = "No location provided"
        elif fifthAddressUnencoded[0] == ',':
            fifthAddressUnencoded = fifthPDescription["City"] + ", " + fifthPDescription["State"] + " " + str(int(fifthPDescription["ZIP"]))
    return winningAddress, winningAddressUnencoded, secondAddress, secondAddressUnencoded, thirdAddress, thirdAddressUnencoded, fourthAddress, fourthAddressUnencoded, fifthAddress, fifthAddressUnencoded

# index page
@app.route('/', methods=['POST', 'GET'])
def msg():
    return render_template('index.html')

# results page
@app.route('/results', methods=['POST', 'GET'])
def db_search():
    query = request.form['data']

    crossEncoderItems, crossEncoderScoresDict = core_search(query, embedder, corpus, encoding_dict)
    winningPDescription, secondPDescription, thirdPDescription, fourthPDescription, fifthPDescription, winningName, secondName, thirdName, fourthName, fifthName, winningDescription, secondDescription, thirdDescription, fourthDescription, fifthDescription, winningWorkPhone, secondWorkPhone, thirdWorkPhone, fourthWorkPhone, fifthWorkPhone, winningConfidence, secondConfidence, thirdConfidence, fourthConfidence, fifthConfidence = grab_info(crossEncoderItems, crossEncoderScoresDict, collection_name)

    
    winningAddress, winningAddressUnencoded, secondAddress, secondAddressUnencoded, thirdAddress, thirdAddressUnencoded, fourthAddress, fourthAddressUnencoded, fifthAddress, fifthAddressUnencoded = create_addresses(winningPDescription, secondPDescription, thirdPDescription, fourthPDescription, fifthPDescription)
    return render_template('results.html',
                            userQuery = query,
                            winnername = winningName,
                            secondname = secondName,
                            thirdname = thirdName,
                            fourthname = fourthName,
                            fifthname = fifthName,
                            notFoundMessage = "Unfortunately we did not find any results for your question. Maybe try asking in a different way?",
                            winningDescription = winningDescription,
                            secondDescription = secondDescription,
                            thirdDescription = thirdDescription,
                            fourthDescription = fourthDescription,
                            fifthDescription = fifthDescription,
                            winningConfidence = winningConfidence,
                            secondConfidence = secondConfidence,
                            thirdConfidence = thirdConfidence,
                            fourthConfidence = fourthConfidence,
                            fifthConfidence = fifthConfidence,
                            winningWorkPhone =  winningWorkPhone,
                            secondWorkPhone = secondWorkPhone,
                            thirdWorkPhone = thirdWorkPhone,
                            fourthWorkPhone = fourthWorkPhone,
                            fifthWorkPhone = fifthWorkPhone,
                            winningAddress = winningAddress,
                            winningAddressUnencoded = winningAddressUnencoded,
                            secondAddress = secondAddress,
                            secondAddressUnencoded = secondAddressUnencoded,
                            thirdAddress = thirdAddress,
                            thirdAddressUnencoded = thirdAddressUnencoded,
                            fourthAddress = fourthAddress,
                            fourthAddressUnencoded = fourthAddressUnencoded,
                            fifthAddress = fifthAddress,
                            fifthAddressUnencoded = fifthAddressUnencoded)
