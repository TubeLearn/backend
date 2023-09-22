
from pymongo import MongoClient


open_ai_api = "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" # expired
mongoURL = "mongodb+srv://tubelearn:1234@cluster0.s19nica.mongodb.net/?retryWrites=true&w=majority" #currently filled with junk
client = MongoClient(mongoURL)
db = client["HackTheClassRoom"]
users_collection = db["users"]
courses_collection = db["courses"]