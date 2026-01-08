from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['cleaning-app']

Students = db['students']
Classes = db['classes']
Admins = db['admins']
