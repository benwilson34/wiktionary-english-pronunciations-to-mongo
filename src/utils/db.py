from pymongo import MongoClient

CONNECTION_STRING = 'mongodb://localhost:27017'

client = MongoClient(CONNECTION_STRING)
db = client['butchr']
collection = db['pronunciations']

def deleteAllWordData():
    collection.delete_many({})

def insertWordData(wordData):
    collection.insert_many(wordData)

def tryGetWordData(word):
    # TODO better search
    return collection.find_one({ 'pageTitle': { '$regex': f'^{word}$', '$options': 'i' } })

print('done')
