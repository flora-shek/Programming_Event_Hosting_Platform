from pymongo import MongoClient
CONNECTION_STRING = 'mongodb+srv://florashek24:5aujbLlxkX76pbxh@uta-enrollment.7dmnt.mongodb.net/?retryWrites=true&w=majority&appName=UTA-Enrollment'

client = MongoClient(CONNECTION_STRING)
mongo_db = client['codecheck']




