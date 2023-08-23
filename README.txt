Intelligent Child System 

Architecture Diagrams:
![Architecture Diagram - Corpus Encoding](https://ibb.co/k4T1G3J)
![Architectre Diagram - Running A Query](https://ibb.co/q15Qg6F)

Terminology
Language Model: a deep learning model that models the probabilistic distribution of a language. Examples include BERT, GPT, LLaMA
Client: web browser
Server: Flask application (will run on server instance hosted by TEES/TCAT)
NoSQL MongoDB: database that stores all documents in the corpus
Github Repository
Deployment
	In order to host this application locally or on a server, the proper environment must first be set up. This can be accomplished by using pip installs (currently using Python v.3.9) after creating a python virtual environment (venv). 

	Necessary packages:
Flask (web framework), version 2.2.3
Pymongo (MongoDB integration), version 4.3.3
Sentence_transformers (NLP engine), version 2.2.2
PyTorch, version 1.13.1
NumPy, version 1.24.2
Coverage (for testing), version 7.2.5
flask_unittest (for testing), version 0.1.3
Functionality
	Currently, the functionality of the application is limited to searching and displaying results from the database on the frontend hosted via flask. The important files to note are:
db_search.py: holds the logic for running the NLP searches, contains links to the training models
results.html: holds some of the logic for determining which results are displayed based on confidence score
Index.html: contains search page/homepage 
sberttraining.py: allows for training of the model. For more information, please visit the documentation at https://www.sbert.net/
unit_testing.py: holds the unit tests for the application 
CHILD_Working_DB_v2 - Sheet1.csv: CSV of all of the data in the database
databaseInsertionTest.py: inserts CHILD_Working_DB_v2 into the database of the application
Searchclient.py - Cut down version of the original program used for testing

In order to host the application locally, run the following command in the same location as the dbsearch.py file (which is currently the search directory):

	flask –-app db_search run 
	
Database
	The data is currently stored in an Atlas MongoDB, which is a noSQL database hosted on the cloud. The connection string for the database located in the dbsearch function is: 

'mongodb+srv://Capstone:ProfWade2023@cluster0.9c4phbt.mongodb.net/?retryWrites=true&w=majority'

The database contains a few different “collections”, with the “Preprocess” collection being pulled in order to encode the corpus. This collection contains all the information of each resource that was provided to us (name, location, description,...) along with a preprocessed description used for encoding. 

In order to access the database using a GUI, download MongoDB Compass and connect using the string:

 mongodb+srv://Capstone:ProfWade2023@cluster0.9c4phbt.mongodb.net/test. 

To add data to the database, we provide a file DatabaseInsertionTest.py where any CSV file named CHILD_Working_DB_v2 - Sheet1.csv located in the data directory is inserted into the database. This overrides all previous data in the database.

Testing
	To test our project we provide a file called unit_testing.py located in the unit testing directory. In this file, we test several aspects of our application, such as the core search method, the method for creating addresses, along with a few others. The file searchclient.py holds the functions being tested. To run these tests type the command (while in the unit testing directory):
	coverage run -m unittest unit_testing.py
To view the code coverage run the command:
	coverage report -m
To view the code coverage in a nicely formatted html file, run the command:
	coverage html
And the file unit testing/htmlcov/index.html holds the coverage information. 
	You will need to update unit_testing.py and searchclient.py as you make changes to the code.
Model and Training
The model used is the Sbert model, a python NLP implementation of the BERT language model from Google. 

The process of embedding and running an NLP search is as follows (all within dbsearch.py):

The corpus is pulled from the database and run through the bi-encoder, embedding the words of each resource’s “pdescription”, which is a preprocessed description containing a resources location, name, and overall description. This encoded resource list is stored in the server.
The user’s query is input and run through the bi-encoder, then stored as an encoded query in the server.
The encoded query is compared to each encoded resource via cosine similarity, returning the top five results with the highest similarity score
The top five resources are sent to the cross-encoder, reranking them by cosine similarity
The top five ordered resources are displayed.

Training the model can be completed by running sberttraining.py, which takes a csv as an input. Each row in the csv must contain three cells - (query, resource description, confidence score). The confidence score is a rating between 0-1 which represents how accurate the resource description is to the query. Resources that had a high likelihood of being able to directly provide help with a given situation were rated between 0.8 and 1.0. Resources that might not be able to directly provide help, but would likely have the necessary connections to quickly direct users to help, were rated between 0.4 and 0.79. Resources that had no relation to a given query were rated between 0.0 and 0.39.
The data is formatted as a CSV, with all prompts located in the first column, the descriptions for the provided answers located in the second column, and the manually provided similarity score located in the third column.
Some example query/response/similarity score data is shown below:

Example 1:

(I'm having trouble breast-feeding my new baby,
Provides medical care during pregnancy. Some basic services provided include physical examinations, distribution of prenatal vitamins, and laboratory work. Other services may also be available; however, other services are provided on an as needed basis to be determined by the nurse practitioners and physician staff who volunteer at the clinic. The clinic offers a comprehensive prenatal program that includes:Prenatal NutritionPhysical/emotional changes during pregnancy and birth Prenatal and postpartum exercise Preparation for labor and birth Parenting skills Breast-feeding Newborn care and feeding,
0.9)



Example 2:

(I think I might have covid, where should I go?,
Provides medical care during pregnancy. Some basic services provided include physical examinations, distribution of prenatal vitamins, and laboratory work. Other services may also be available; however, other services are provided on an as needed basis to be determined by the nurse practitioners and physician staff who volunteer at the clinic. The clinic offers a comprehensive prenatal program that includes:Prenatal NutritionPhysical/emotional changes during pregnancy and birth Prenatal and postpartum exercise Preparation for labor and birth Parenting skills Breast-feeding Newborn care and feeding,
0.4)


