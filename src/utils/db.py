from pymongo import MongoClient

CONNECTION_STRING = 'mongodb://localhost:27017'

client = MongoClient(CONNECTION_STRING)
db = client['enwiktionary']
collection = db['pronuns']

def deleteAllWordData():
    collection.delete_many({})

def insertWordData(wordData):
    collection.insert_many(wordData)
